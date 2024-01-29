import asyncio
import dataclasses
from datetime import datetime, date
from typing import Any, Literal, Optional
from type_converter import convert_to_column_type
from app.models.warehouse.dbt_quickbooks import t_quickbooks__ap_ar_enhanced

from app.database import DBManager
from app.models.fivetranschema import FivetranSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, Executable, table, column, ColumnElement, func, inspect, bindparam, Table
import pandas as pd
import numpy as np
from app.models.warehouse import t_quickbooks__balance_sheet, t_sage_intacct__balance_sheet, \
    t_xero__balance_sheet_report, \
    t_sage_intacct__ap_ar_enhanced, t_xero__invoice_line_items, t_quickbooks__ap_ar_enhanced, \
    t_sage_intacct__profit_and_loss, \
    t_quickbooks__profit_and_loss, t_xero__profit_and_loss_report


async def build_schemas(db_session: AsyncSession, tenant_id) -> dict[str, FivetranSchema]:
    """Builds a list of FivetranSchema objects available for querying."""
    # Select all schemas from the FivetranSchema table where the tenant_id matches
    result = await db_session.execute(select(FivetranSchema).where(FivetranSchema.tenant_id == tenant_id))

    # Fetch all results as FivetranSchema objects
    fivetran_schemas = result.scalars().all()
    return {schema.schema_name: schema for schema in fivetran_schemas}


async def query_clause_builder(self, **kwargs) -> tuple[str, tuple]:
    """
    Build a WHERE clause for an SQL query based on provided keyword arguments.
    Supports parameterization with placeholders like $1, $2, etc.
    Returns both the WHERE clause and a tuple of parameters.

    Args:
    **kwargs: Arbitrary keyword arguments.
              Key represents the column name, value represents the search value.

    Returns:
    A tuple (where_clause, parameters), where:
    - where_clause is a string representing the WHERE clause of an SQL query.
    - parameters is a tuple containing the values in the order they appear in the clause.
    """

    clauses = []
    parameters = []
    param_index = 1

    for key, value in kwargs.items():
        if value is None:
            continue  # Skip null values

        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, datetime) for v in value):
            # Handle BETWEEN clause for datetime range
            clauses.append(f"{key} BETWEEN :start_date AND :end_date")
            parameters.extend(value)
        else:
            # Handle standard equality clause
            clauses.append(f"{key} = :{key}")
            parameters.append(value)
            param_index += 1

    where_clause = ' AND '.join(clauses)
    return where_clause, tuple(parameters)


def convert_dates_to_excel_int(df, system):
    # Set the epoch based on the system type
    if system.lower() == 'mac':
        datetime_epoch = datetime(1904, 1, 1)
        date_epoch = date(1904, 1, 1)
    else:  # default to Windows
        datetime_epoch = datetime(1899, 12, 30)
        date_epoch = date(1899, 12, 30)

    for col in df.columns:
        # Check if the column has datetime64, datetime.date, or datetime.datetime dtype
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(lambda x:
                                    (pd.Timestamp(x) - datetime_epoch).days +
                                    (pd.Timestamp(x) - datetime_epoch).total_seconds() % 86400 / 86400
                                    if pd.notnull(x) else np.nan)
        elif isinstance(df[col].iloc[0], date):
            # Convert to Excel date format (only date part, no time)
            df[col] = df[col].apply(lambda x: (x - date_epoch).days if isinstance(x, date) else np.nan)
        elif isinstance(df[col].iloc[0], datetime):
            df[col] = df[col].apply(lambda x: (x - datetime_epoch).seconds if isinstance(x, datetime) else np.nan)
        return df


@dataclasses.dataclass
class Response:
    status: Literal['success', 'error']
    type: Literal['scalar', 'tabular']
    value: Any


class CustomFunctionHandler:
    def __init__(self, wh_session: DBManager, platform: str, query_batch: list[dict],
                 schemas: dict[str, FivetranSchema], tenant_db: str, redis):
        self.wh_session = wh_session
        self.platform = platform
        self.query_batch = query_batch
        self.schemas = schemas
        self.tenant_db = tenant_db
        self.redis = redis

    async def scalar_query(self, stmt: Executable, schema_ref: str) -> any:
        cache_key = f"{self.tenant_db}_{schema_ref}_{stmt}"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return cached_data
        else:
            db_session = self.wh_session.get_session()
            await db_session.execute(text(f"SET search_path TO {schema_ref}"))
            result = await db_session.execute(stmt)
            data = await result.scalar()
            await self.redis.set(cache_key, data, ex=300)
            return data

    async def tabular_query(self, stmt: Executable, schema_ref: str) -> str:
        # check if sql query is in redis cache
        cache_key = f"{self.tenant_db}_{schema_ref}_{stmt}"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return cached_data
        else:
            db_session = self.wh_session.get_session()
            await db_session.execute(text(f"SET search_path TO {schema_ref}"))
            result = await db_session.execute(stmt)
            result = result.fetchall()
            df = pd.DataFrame(result)
            data = df.to_json(orient='split', date_format='iso')
            await self.redis.set(cache_key, data, ex=300)
            return df.to_json(orient='split', date_format='iso')

    async def execute(self) -> tuple[Any]:
        coroutines = [getattr(self, query['operation'])(**query['args']) for query in self.query_batch]
        return await asyncio.gather(*coroutines)

    async def excel_date_to_datetime(self, excel_date: int) -> datetime:
        """Convert an Excel date number to a Python datetime object. Based on office platform."""
        if self.platform == 'PC':
            return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + excel_date - 2)
        elif self.platform == 'MAC':
            return datetime.fromordinal(datetime(1904, 1, 1).toordinal() + excel_date - 2)
        else:
            raise ValueError('Invalid platform')

    async def period_to_date_range(self, excel_date: int, period: str) -> tuple[datetime, datetime]:
        """Converts an Excel date and period ('YTD', 'QTD', 'MTD') to an ISO date range."""
        base_date = await self.excel_date_to_datetime(excel_date)

        if period == 'YTD':
            start_date = datetime(base_date.year, 1, 1)
        elif period == 'QTD':
            quarter = (base_date.month - 1) // 3 + 1
            start_month = 3 * quarter - 2
            start_date = datetime(base_date.year, start_month, 1)
        elif period == 'MTD':
            start_date = datetime(base_date.year, base_date.month, 1)
        else:
            raise ValueError('Invalid period')

        end_date = base_date
        return start_date, end_date

    async def trial_balance(self, schema_name: str, period_last_day: int,
                            period: Literal["MTD", "QTD", "YTD"]) -> Response:
        """Returns a two-dimensional array of monthly account balances for a given period."""
        start_date, end_date = await self.period_to_date_range(period_last_day, period)
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source == 'sage_intacct':  # Add other sources as needed
                sql = '''SELECT * FROM sage_intacct__general_ledger_by_period WHERE period_last_day between :start and :end'''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date)

            elif source == 'quickbooks':
                sql = '''SELECT * FROM quickbooks__general_ledger_by_period WHERE period_last_day between :start and :end'''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date)

            elif source == 'xero':
                raise ValueError('xero does not support trial balance queries. Use profit_and_loss or balance_sheet')
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def profit_and_loss(self, schema_name: str,
                              month: int,
                              period: Literal["MTD", "QTD", "YTD"]) -> Response:
        """Returns a two-dimensional array of income statement balances for a given period."""
        start_date, end_date = await self.period_to_date_range(month, period)
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source == 'sage_intacct':  # Add other sources as needed
                sql = '''SELECT period_date,
                               account_no,
                               account_title,
                               account_type,
                               book_id,
                               category,
                               classification,
                               currency,
                               entry_state,
                               sum(amount) as total
                        FROM sage_intacct__profit_and_loss
                        WHERE period_date between :start and :end
                        GROUP BY period_date, account_no, account_title, account_type, book_id, category, classification, currency, entry_state
                      '''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date)
            elif source == 'quickbooks':
                sql = '''SELECT calendar_date,
                               source_relation,
                               account_class,
                               class_id,
                               is_sub_account,
                               parent_account_number,
                               parent_account_name,
                               account_type,
                               account_sub_type,
                               account_number,
                               account_id,
                               account_name,
                               sum(amount) as total
                        FROM quickbooks__profit_and_loss
                        WHERE calendar_date between :start and :end
                        GROUP BY calendar_date, source_relation, account_class, class_id, is_sub_account, parent_account_number,
                                 parent_account_name, account_type, account_sub_type, account_number, account_id, account_name
                       '''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date)
            elif source == 'xero':
                sql = '''SELECT profit_and_loss_id, date_month, account_id, account_name, account_code, account_type, account_class, source_relation, sum(net_amount) as total 
                         FROM xero__profit_and_loss_report
                         WHERE date_month between :start and :end
                         GROUP BY profit_and_loss_id, date_month, account_id, account_name, account_code, account_type, account_class, source_relation'''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date)
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def balance_sheet(self, schema_name: str,
                            month: int) -> Response:
        """Returns a two-dimensional array of balance sheet balances for a given period."""
        start_date, end_date = await self.period_to_date_range(month, "MTD")
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source == 'sage_intacct':  # Add other sources as needed
                # define the table
                sql = '''SELECT * FROM sage_intacct__balance_sheet WHERE period_date = :start_date'''
                query = text(sql)
                query.bindparams(start_date=start_date)
            elif source == 'quickbooks':
                sql = '''SELECT * FROM quickbooks__balance_sheet WHERE calendar_date = :start_date'''
                query = text(sql)
                query.bindparams(start_date=start_date)
            elif source == 'xero':
                sql = '''SELECT * FROM xero__balance_sheet_report WHERE date_month = :start_date'''
                query = text(sql)
                query.bindparams(start_date=start_date)
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def ap(self, schema_name: str, entry_date: int, period: Literal["MTD", "QTD", "YTD"],
                 vendor_id: str) -> Response:
        """Returns a two-dimensional array of accounts payable balances for a given period."""
        start_date, end_date = await self.period_to_date_range(entry_date, period)
        schema_ref = self.schemas[schema_name].build_dbt_schema()
        source = self.schemas[schema_name].source
        if source == 'sage_intacct':
            query = select(t_sage_intacct__ap_ar_enhanced).where(
                t_sage_intacct__ap_ar_enhanced.c.entry_date_at.between(start_date, end_date),
                t_sage_intacct__ap_ar_enhanced.c.document_type == 'bill')
            if vendor_id:
                query = query.where(t_sage_intacct__ap_ar_enhanced.c.vendor_id == vendor_id)
        if source == 'quickbooks':
            query = select(t_quickbooks__ap_ar_enhanced).where(
                t_quickbooks__ap_ar_enhanced.c.entry_date_at.between(start_date, end_date),
                t_quickbooks__ap_ar_enhanced.c.document_type == 'bill')
            if vendor_id:
                query = query.where(t_quickbooks__ap_ar_enhanced.c.customer_vendor_name == vendor_id)
        if source == 'xero':
            query = select(t_xero__invoice_line_items).where(
                t_xero__invoice_line_items.c.invoice_date.between(start_date, end_date),
                t_xero__invoice_line_items.c.invoice_type == 'ACCPAY')
            if vendor_id:
                query = query.where(t_xero__invoice_line_items.c.contact_name == vendor_id)
        else:
            raise ValueError('unsupported source')
        try:
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def ar(self, schema_name: str, entry_date: int, period: Literal["MTD", "QTD", "YTD"],
                 customer_id: str) -> Response:
        """Returns a two-dimensional array of accounts payable balances for a given period."""
        start_date, end_date = await self.period_to_date_range(entry_date, period)
        schema_ref = self.schemas[schema_name].build_dbt_schema()
        source = self.schemas[schema_name].source
        if source == 'sage_intacct':
            query = select(t_sage_intacct__ap_ar_enhanced).where(
                t_sage_intacct__ap_ar_enhanced.c.entry_date_at.between(start_date, end_date),
                t_sage_intacct__ap_ar_enhanced.c.document_type == 'invoice')
            if customer_id:
                query = query.where(t_sage_intacct__ap_ar_enhanced.c.vendor_id == customer_id)
        if source == 'quickbooks':
            query = select(t_quickbooks__ap_ar_enhanced).where(
                t_quickbooks__ap_ar_enhanced.c.entry_date_at.between(start_date, end_date),
                t_quickbooks__ap_ar_enhanced.c.document_type == 'invoice')
            if customer_id:
                query = query.where(t_quickbooks__ap_ar_enhanced.c.customer_vendor_name == customer_id)
        if source == 'xero':
            query = select(t_xero__invoice_line_items).where(
                t_xero__invoice_line_items.c.invoice_date.between(start_date, end_date),
                t_xero__invoice_line_items.c.invoice_type == 'ACCREC')
            if customer_id:
                query = query.where(t_xero__invoice_line_items.c.contact_name == customer_id)
        else:
            raise ValueError('unsupported source')
        try:
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def bs_acct(self, schema_name: str, month: int, filter_col: str, filter_val: any) -> Response:
        """Returns a scalar value representing the account balance for a given period."""
        start_date, end_date = await self.period_to_date_range(month, "MTD")
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            filter_col = filter_col.lower().split(' ', 1)[0]
            if source == 'sage_intacct':  # Add other sources as needed
                filter_val = convert_to_column_type(t_sage_intacct__balance_sheet, filter_col, filter_val)
                sql = f'''SELECT sum(amount) FROM sage_intacct__balance_sheet WHERE period_date = :start_date and {filter_col} = :filter_val'''
                query = text(sql)

                query.bindparams(start_date=start_date, filter_val=filter_val)
            elif source == 'quickbooks':
                filter_val = convert_to_column_type(t_quickbooks__balance_sheet, filter_col, filter_val)
                sql = f'''SELECT * FROM quickbooks__balance_sheet WHERE calendar_date = :start_date and {filter_col} = :filter_val'''
                query = text(sql)
                query.bindparams(start_date=start_date, filter_val=filter_val)
            elif source == 'xero':
                filter_val = convert_to_column_type(t_xero__balance_sheet_report, filter_col, filter_val)
                sql = f'''SELECT * FROM xero__balance_sheet_report WHERE date_month = :start_date and {filter_col} = :filter_val'''
                query = text(sql)
                query.bindparams(start_date=start_date, filter_val=filter_val)
            else:
                raise ValueError('unsupported source')
            value = await self.scalar_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def pl_acct(self, schema_name: str, entry_date: int,
                      period: Literal["MTD", "QTD", "YTD"], filter_col: str, filter_val: any) -> Response:
        """Returns a scalar value representing the account balance for a given period."""
        start_date, end_date = await self.period_to_date_range(entry_date, period)
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            filter_col = filter_col.lower().split(' ', 1)[0]
            if source == 'sage_intacct':  # Add other sources as needed
                filter_val = convert_to_column_type(t_sage_intacct__profit_and_loss, filter_col, filter_val)
                sql = f'''SELECT 
                               sum(amount) as total
                        FROM sage_intacct__profit_and_loss
                        WHERE period_date between :start and :end and {filter_col} = :filter_val
                      '''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date, filter_val=filter_val)
            elif source == 'quickbooks':
                filter_val = convert_to_column_type(t_quickbooks__profit_and_loss, filter_col, filter_val)
                sql = f'''SELECT 
                               sum(amount) as total
                        FROM quickbooks__profit_and_loss
                        WHERE calendar_date between :start and :end and {filter_col} = :filter_val
                       '''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date, filter_val=filter_val)
            elif source == 'xero':
                sql = f'''SELECT sum(net_amount) as total 
                         FROM xero__profit_and_loss_report
                         WHERE date_month between :start and :end and {filter_col} = :filter_val'''
                query = text(sql)
                query = query.bindparams(start=start_date, end=end_date, filter_val=filter_val)
            else:
                raise ValueError('unsupported source')
            value = await self.scalar_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def sage_acct_bal(self, schema_name: str, entry_date: int,
                            period: Literal["MTD", "QTD", "YTD"], account_no: str, location_id: Optional[str] = None,
                            department_id: Optional[int] = None) -> Response:
        """Returns a scalar value representing the account balance for a given period."""

        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            sql = '''SELECT accounttype from gl_account where accountno = :account_no'''
            query = text(sql)
            value = await self.scalar_query(query, schema_ref)
            start_date, end_date = await self.period_to_date_range(entry_date, period)
            if value == 'balancesheet' and location_id or department_id:
                raise ValueError('location_id and department_id are not supported for balance sheet accounts')
            # Base query construction
            table_map = {
                'balancesheet': 'sage_intacct__balance_sheet',
                'incomestatement': 'sage_intacct__general_ledger'
            }
            sql_base = f'''SELECT sum(amount) as total from {table_map.get(value, 'default_table')} WHERE period_date = :start_date and account_no = :account_no'''

            # Dynamic WHERE clause construction
            where_clauses = []
            params = {'start_date': start_date, 'account_no': account_no}

            if location_id:
                where_clauses.append('location_id = :location_id')
                params['location_id'] = location_id

            if department_id:
                where_clauses.append('department_id = :department_id')
                params['department_id'] = department_id

            if where_clauses:
                sql_base += ' and ' + ' and '.join(where_clauses)

            query = text(sql_base).bindparams(**params)
            value = await self.scalar_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def sage_gl_detail(self, schema_name: str, entry_date: int, period: Literal["MTD", "QTD", "YTD"], account_no: str, location_id: Optional[str] = None, department_id: Optional[int] = None) -> Response:
        """Returns a scalar value representing the account balance for a given period."""
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            sql = '''SELECT accounttype from gl_account where accountno = :account_no'''
            query = text(sql)
            value = await self.scalar_query(query, schema_ref)
            start_date, end_date = await self.period_to_date_range(entry_date, period)
            sql_base = f'''SELECT * from sage_intacct__general_ledger WHERE period_date = :start_date and account_no = :account_no'''

            # Dynamic WHERE clause construction
            where_clauses = []
            params = {'start_date': start_date, 'account_no': account_no}

            if location_id:
                where_clauses.append('location_id = :location_id')
                params['location_id'] = location_id

            if department_id:
                where_clauses.append('department_id = :department_id')
                params['department_id'] = department_id

            if where_clauses:
                sql_base += ' and ' + ' and '.join(where_clauses)

            query = text(sql_base).bindparams(**params)
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def employee(self, schema_name: str, active: bool = True):
        """Returns a two-dimensional array of employees for intacct"""
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source in ('sage_intacct', 'quickbooks', 'xero'):
                if active:
                    sql = '''SELECT * FROM employee where active = true'''
                    query = text(sql)
                    query = query.bindparams(active=active)
                else:
                    sql = '''SELECT * FROM employee'''
                    query = text(sql)
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def vendor(self, schema_name: str, active: bool = True) -> Response:
        """Returns a two-dimensional array of vendors for a given period."""
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source in ('sage_intacct', 'quickbooks'):
                if active:
                    sql = '''SELECT * FROM vendor where active = true'''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM vendor'''
                    query = text(sql)
            elif source == 'xero':
                if active:
                    sql = '''SELECT * FROM contact where is_supplier = true and is_customer = false and contact_status = 'ACTIVE' '''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM contact where is_supplier = true and is_customer = false'''
                    query = text(sql)
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def customer(self, schema_name: str, active: bool) -> Response:
        """returns a two-dimensional array of customers for a given period."""
        try:
            schema_ref = self.schemas[schema_name].build_dbt_schema()
            source = self.schemas[schema_name].source
            if source in ('sage_intacct', 'quickbooks'):
                if active:
                    sql = '''SELECT * FROM customer where active = true'''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM customer'''
                    query = text(sql)
            elif source == 'xero':
                if active:
                    sql = '''SELECT * FROM contact where is_supplier = true and is_customer = false and contact_status = 'ACTIVE' '''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM contact where is_supplier = true and is_customer = false'''
                    query = text(sql)
            else:
                raise ValueError('unsupported source')
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)

        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def accts(self, schema_name: str, active: bool) -> Response:
        """returns a two-dimensional array of accounts for intacct"""
        schema_ref = self.schemas[schema_name].build_dbt_schema()
        source = self.schemas[schema_name].source
        try:
            if source == 'sage_intacct':
                if active:
                    sql = '''SELECT * FROM gl_account where status = 'active' '''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM gl_account'''
                    query = text(sql)
            elif source == 'quickbooks':
                if active:
                    sql = '''SELECT * FROM account where active = true'''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM account'''
                    query = text(sql)
            elif source == 'xero':
                if active:
                    sql = '''SELECT * FROM account where status = 'ACTIVE' '''
                    query = text(sql)
                else:
                    sql = '''SELECT * FROM account'''
                    query = text(sql)
            value = await self.tabular_query(query, schema_ref)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def get_table(self, schema_name, table_name: str) -> Response:
        """Returns a two-dimensional array of the selected object for a given period."""
        # TODO add table validation to prevent sql injection
        tbl = table(table_name)
        query = select(text('*'), tbl)
        try:
            value = await self.tabular_query(query, schema_name)
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def get_objects(self, schema_name: str) -> Response:
        """Returns a list of objects available for querying."""
        tbl = table('tables')
        query = select(text('table_name'), tbl).where(column('table_schema').__eq__(schema_name))
        try:
            value = await self.tabular_query(query, 'information_schema')
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))

    async def get_schemas(self) -> Response:
        """Returns a list of schemas available for querying."""
        try:
            tbl = table('schemata')
            query = select(text('schema_name'), tbl)
            value = await self.tabular_query(query, 'information_schema')
            return Response(status='success', type='tabular', value=value)
        except Exception as e:
            return Response(status='error', type='scalar', value=str(e))
