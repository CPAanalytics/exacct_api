from sqlalchemy import Text
from sqlalchemy.sql.sqltypes import Date, Integer, Numeric, String, Boolean
from datetime import datetime
import decimal


def convert_to_column_type(table, column_name, value):
    # Find the column in the table
    column = table.columns.get(column_name)
    if column is None:
        raise ValueError(f"Column '{column_name}' not found in the table")

    # Determine the column type and convert the value accordingly
    if isinstance(column.type, Integer):
        return int(value)
    elif isinstance(column.type, Numeric):
        return decimal.Decimal(value)
    elif isinstance(column.type, String) or isinstance(column.type, Text):
        return str(value)
    elif isinstance(column.type, Date):
        # Assuming the date format in the string is YYYY-MM-DD
        return datetime.strptime(value, "%Y-%m-%d").date()
    elif isinstance(column.type, Boolean):
        return value.lower() in ['true', '1', 'yes']
    else:
        raise TypeError(f"Unsupported column type: {type(column.type)}")
