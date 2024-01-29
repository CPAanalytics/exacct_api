from sqlalchemy import Boolean, Column, Date, DateTime, Integer, MetaData, Numeric, String, Table, Text
from sqlalchemy.orm.base import Mapped

metadata = MetaData()


t_xero__balance_sheet_report = Table(
    'xero__balance_sheet_report', metadata,
    Column('date_month', Date),
    Column('account_name', String),
    Column('account_code', String),
    Column('account_id', String),
    Column('account_type', String),
    Column('account_class', String),
    Column('source_relation', Text),
    Column('net_amount', Numeric),
    
)

t_xero__general_ledger = Table(
    'xero__general_ledger', metadata,
    Column('journal_id', String(256)),
    Column('created_date_utc', DateTime(True)),
    Column('journal_date', Date),
    Column('journal_number', Integer),
    Column('reference', String(256)),
    Column('source_id', String(256)),
    Column('source_type', String(256)),
    Column('source_relation', Text),
    Column('journal_line_id', String(256)),
    Column('account_code', String(256)),
    Column('account_id', String(256)),
    Column('account_name', String(256)),
    Column('account_type', String(256)),
    Column('description', String(512)),
    Column('gross_amount', Numeric(18, 6)),
    Column('net_amount', Numeric(18, 6)),
    Column('tax_amount', Numeric(18, 6)),
    Column('tax_name', String(256)),
    Column('tax_type', String(256)),
    Column('account_class', String(256)),
    Column('invoice_id', String),
    Column('bank_transaction_id', String),
    Column('bank_transfer_id', String),
    Column('manual_journal_id', String),
    Column('payment_id', String),
    Column('credit_note_id', String),
    Column('contact_id', String(256)),
    Column('contact_name', String(256)),
    
)

t_xero__invoice_line_items = Table(
    'xero__invoice_line_items', metadata,
    Column('_fivetran_synced', DateTime(True)),
    Column('account_code', String(256)),
    Column('line_item_description', String(512)),
    Column('discount_entered_as_percent', Boolean),
    Column('discount_rate', Integer),
    Column('invoice_id', String(128)),
    Column('item_code', String(256)),
    Column('line_amount', Numeric(18, 6)),
    Column('line_item_id', String(256)),
    Column('quantity', Numeric(18, 2)),
    Column('tax_amount', Numeric(18, 6)),
    Column('tax_type', String(256)),
    Column('unit_amount', Numeric(18, 6)),
    Column('source_relation', Text),
    Column('invoice_date', Date),
    Column('updated_date', DateTime(True)),
    Column('planned_payment_date', DateTime(True)),
    Column('due_date', Date),
    Column('expected_payment_date', DateTime(True)),
    Column('fully_paid_on_date', Date),
    Column('currency_code', String(256)),
    Column('currency_rate', Numeric(18, 6)),
    Column('invoice_number', String(256)),
    Column('is_sent_to_contact', Boolean),
    Column('invoice_status', String(256)),
    Column('type', String(256)),
    Column('url', String(256)),
    Column('invoice_reference', String(256)),
    Column('account_id', String(256)),
    Column('account_name', String(256)),
    Column('account_type', String(256)),
    Column('account_class', String(256)),
    Column('contact_name', String(256)),
    
)

t_xero__profit_and_loss_report = Table(
    'xero__profit_and_loss_report', metadata,
    Column('profit_and_loss_id', Text),
    Column('date_month', Date),
    Column('account_id', String(256)),
    Column('account_name', String(256)),
    Column('account_code', String(256)),
    Column('account_type', String(256)),
    Column('account_class', String(256)),
    Column('source_relation', Text),
    Column('net_amount', Numeric),
    
)
