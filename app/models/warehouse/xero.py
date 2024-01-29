from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Double, Integer, MetaData, Numeric, PrimaryKeyConstraint, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.base import Mapped

metadata = MetaData()


t_account = Table(
    'account', metadata,
    Column('account_id', String(256)),
    Column('add_to_watchlist', Boolean),
    Column('code', String(256)),
    Column('name', String(256)),
    Column('type', String(256)),
    Column('description', String(512)),
    Column('tax_type', String(256)),
    Column('enable_payments_to_account', Boolean),
    Column('show_in_expense_claims', Boolean),
    Column('class', String(256)),
    Column('status', String(256)),
    Column('system_account', String(256)),
    Column('bank_account_type', String(256)),
    Column('bank_account_number', String(256)),
    Column('currency_code', String(256)),
    Column('reporting_code', String(256)),
    Column('reporting_code_name', String(256)),
    Column('has_attachments', Boolean),
    Column('updated_date_utc', DateTime(True)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('account_id', name='account_pkey'),
    
)

t_allocation = Table(
    'allocation', metadata,
    Column('allocation_id', String(256), nullable=False),
    Column('index', BigInteger, nullable=False),
    Column('credit_note_id', String(256)),
    Column('overpayment_id', String(256)),
    Column('prepayment_id', String(256)),
    Column('amount', Numeric(18, 6)),
    Column('date', Date),
    Column('invoice_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('allocation_id', 'index', name='allocation_pkey'),
    
)

t_asset = Table(
    'asset', metadata,
    Column('id', String(256)),
    Column('asset_type_id', String(256)),
    Column('asset_name', String(256)),
    Column('asset_number', String(256)),
    Column('purchase_price', Numeric(18, 4)),
    Column('serial_number', String(256)),
    Column('purchase_date', DateTime(True)),
    Column('warranty_expiry_date', DateTime(True)),
    Column('disposal_date', DateTime(True)),
    Column('description', String(256)),
    Column('disposal_price', Numeric(18, 4)),
    Column('asset_status', String(256)),
    Column('can_rollback', Boolean),
    Column('accounting_book_value', Numeric(18, 6)),
    Column('is_delete_enabled_for_date', Boolean),
    Column('depreciation_book_effective_date_of_change_id', String(256)),
    Column('depreciation_effective_life_years', Numeric(18, 2)),
    Column('depreciation_averaging_method', String(256)),
    Column('depreciation_effective_from_date', DateTime(True)),
    Column('depreciation_object_id', String(256)),
    Column('depreciation_object_type', String(256)),
    Column('depreciation_method', String(256)),
    Column('depreciation_rate', Integer),
    Column('depreciation_calculation_method', String(256)),
    Column('depreciation_current_capital_gain', Numeric(18, 6)),
    Column('depreciation_current_gain_loss', Numeric(18, 6)),
    Column('prior_accum_depreciation_amount', Numeric(18, 6)),
    Column('current_accum_depreciation_amount', Numeric(18, 6)),
    Column('depreciation_start_date', DateTime(True)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('id', name='asset_pkey'),
    
)

t_asset_type = Table(
    'asset_type', metadata,
    Column('asset_type_id', String(256)),
    Column('asset_type_name', String(256)),
    Column('fixed_asset_account_id', String(256)),
    Column('depreciation_expense_account_id', String(256)),
    Column('accumulated_depreciation_account_id', String(256)),
    Column('locks', Integer),
    Column('lock_private_use_account', Boolean),
    Column('depreciation_book_effective_date_of_change_id', String(256)),
    Column('depreciation_effective_life_years', Numeric(18, 2)),
    Column('depreciation_averaging_method', String(256)),
    Column('depreciation_effective_from_date', DateTime(True)),
    Column('depreciation_object_id', String(256)),
    Column('depreciation_object_type', String(256)),
    Column('depreciation_method', String(256)),
    Column('depreciation_rate', Integer),
    Column('depreciation_calculation_method', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('asset_type_id', name='asset_type_pkey'),
    
)

t_bank_account = Table(
    'bank_account', metadata,
    Column('account_id', String(256)),
    Column('code', String(256)),
    Column('name', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('account_id', name='bank_account_pkey'),
    
)

t_bank_transaction = Table(
    'bank_transaction', metadata,
    Column('bank_transaction_id', String(256)),
    Column('type', String(256)),
    Column('status', String(256)),
    Column('reference', String(256)),
    Column('is_reconciled', Boolean),
    Column('has_attachments', Boolean),
    Column('batch_payment_date', DateTime(True)),
    Column('batch_payment_type', String(256)),
    Column('batch_payment_status', String(256)),
    Column('batch_payment_total_amount', Double(53)),
    Column('batch_payment_updated_date_utc', DateTime(True)),
    Column('batch_payment_is_reconciled', Boolean),
    Column('batch_payment_id', String(256)),
    Column('overpayment_id', String(256)),
    Column('prepayment_id', String(256)),
    Column('date', Date),
    Column('line_amount_types', String(256)),
    Column('sub_total', Numeric(18, 6)),
    Column('total_tax', Numeric(18, 6)),
    Column('total', Numeric(18, 6)),
    Column('currency_rate', Numeric(18, 6)),
    Column('updated_date_utc', DateTime(True)),
    Column('currency_code', String(256)),
    Column('url', String(256)),
    Column('external_link_provider_name', String(256)),
    Column('bank_account_id', String(256)),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('bank_transaction_id', name='bank_transaction_pkey'),
    
)

t_bank_transaction_line_item_has_tracking_category = Table(
    'bank_transaction_line_item_has_tracking_category', metadata,
    Column('bank_transaction_id', String(256), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('tracking_category_id', String(256), nullable=False),
    Column('option', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('bank_transaction_id', 'line_item_id', 'tracking_category_id', name='bank_transaction_line_item_has_tracking_category_pkey'),
    
)

t_bank_transaction_line_items = Table(
    'bank_transaction_line_items', metadata,
    Column('bank_transaction_id', String(256), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('description', String(256)),
    Column('quantity', Numeric(18, 2)),
    Column('unit_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('item_code', String(256)),
    Column('tax_type', String(256)),
    Column('tax_amount', Numeric(18, 6)),
    Column('line_amount', Numeric(18, 6)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('bank_transaction_id', 'line_item_id', name='bank_transaction_line_items_pkey'),
    
)

t_branding_theme = Table(
    'branding_theme', metadata,
    Column('branding_theme_id', String(256)),
    Column('name', String(256)),
    Column('sort_order', Integer),
    Column('created_date_utc', DateTime(True)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('branding_theme_id', name='branding_theme_pkey'),
    
)

t_contact = Table(
    'contact', metadata,
    Column('contact_id', String(256)),
    Column('contact_number', String(256)),
    Column('account_number', String(256)),
    Column('contact_status', String(256)),
    Column('name', String(256)),
    Column('first_name', String(256)),
    Column('last_name', String(256)),
    Column('email_address', String(256)),
    Column('skype_user_name', String(256)),
    Column('bank_account_details', String(256)),
    Column('tax_number', String(256)),
    Column('accounts_receivable_tax_type', String(256)),
    Column('accounts_payable_tax_type', String(256)),
    Column('sales_default_account_code', String(256)),
    Column('purchases_default_account_code', String(256)),
    Column('is_supplier', Boolean),
    Column('is_customer', Boolean),
    Column('batch_payments_bank_account_number', String(256)),
    Column('batch_payments_bank_account_name', String(256)),
    Column('batch_payments_details', String(256)),
    Column('batch_payments_code', String(256)),
    Column('batch_payments_reference', String(256)),
    Column('default_currency', String(256)),
    Column('xero_network_key', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('website', String(256)),
    Column('discount', Integer),
    Column('balances_accounts_receivable_outstanding', Numeric(18, 6)),
    Column('balances_accounts_receivable_overdue', Numeric(18, 6)),
    Column('balances_accounts_payable_outstanding', Numeric(18, 6)),
    Column('balances_accounts_payable_overdue', Numeric(18, 6)),
    Column('has_attachments', Boolean),
    Column('has_validation_errors', Boolean),
    Column('branding_theme_id', String(256)),
    Column('_fivetran_deleted', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('contact_id', name='contact_pkey'),
    
)

t_contact_address = Table(
    'contact_address', metadata,
    Column('contact_id', String(256), nullable=False),
    Column('_index', Integer, nullable=False),
    Column('address_type', String(256)),
    Column('address_line_1', String(256)),
    Column('address_line_2', String(256)),
    Column('address_line_3', String(256)),
    Column('address_line_4', String(256)),
    Column('city', String(256)),
    Column('region', String(256)),
    Column('postal_code', String(256)),
    Column('country', String(256)),
    Column('attention_to', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('contact_id', '_index', name='contact_address_pkey'),
    
)

t_contact_group = Table(
    'contact_group', metadata,
    Column('contact_group_id', String(256)),
    Column('name', String(256)),
    Column('status', String(256)),
    Column('has_validation_errors', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('contact_group_id', name='contact_group_pkey'),
    
)

t_contact_group_member = Table(
    'contact_group_member', metadata,
    Column('contact_group_id', String(256), nullable=False),
    Column('contact_id', String(256), nullable=False),
    Column('_fivetran_deleted', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('contact_group_id', 'contact_id', name='contact_group_member_pkey'),
    
)

t_credit_note = Table(
    'credit_note', metadata,
    Column('credit_note_id', String(256)),
    Column('credit_note_number', String(256)),
    Column('currency_rate', Numeric(18, 6)),
    Column('type', String(256)),
    Column('reference', String(256)),
    Column('remaining_credit', Numeric(18, 6)),
    Column('applied_amount', Numeric(18, 6)),
    Column('has_attachments', Boolean),
    Column('date', Date),
    Column('due_date', Date),
    Column('branding_theme_id', String(256)),
    Column('status', String(256)),
    Column('line_amount_types', String(256)),
    Column('sub_total', Numeric(18, 6)),
    Column('total_tax', Numeric(18, 6)),
    Column('total', Numeric(18, 6)),
    Column('updated_date_utc', DateTime(True)),
    Column('currency_code', String(256)),
    Column('fully_paid_on_date', Date),
    Column('sent_to_contact', Boolean),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('credit_note_id', name='credit_note_pkey'),
    
)

t_credit_note_line_item = Table(
    'credit_note_line_item', metadata,
    Column('credit_note_id', String(256), nullable=False),
    Column('line_index', Integer, nullable=False),
    Column('description', String(256)),
    Column('unit_amount', Numeric(18, 6)),
    Column('tax_type', String(256)),
    Column('tax_amount', Numeric(18, 6)),
    Column('line_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('item_code', String(256)),
    Column('discount_entered_as_percent', Boolean),
    Column('quantity', Numeric(18, 2)),
    Column('validation_errors', JSONB),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('credit_note_id', 'line_index', name='credit_note_line_item_pkey'),
    
)

t_credit_note_line_item_has_tracking_category = Table(
    'credit_note_line_item_has_tracking_category', metadata,
    Column('credit_note_id', String(256), nullable=False),
    Column('line_itemindex', Integer, nullable=False),
    Column('tracking_category_id', String(256), nullable=False),
    Column('tracking_category_option_id', String(256)),
    Column('option', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('credit_note_id', 'line_itemindex', 'tracking_category_id', name='credit_note_line_item_has_tracking_category_pkey'),
    
)

t_currency = Table(
    'currency', metadata,
    Column('code', String(256)),
    Column('description', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('code', name='currency_pkey'),
    
)

t_employee = Table(
    'employee', metadata,
    Column('employee_id', String(256)),
    Column('status', String(256)),
    Column('first_name', String(256)),
    Column('last_name', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('employee_id', name='employee_pkey'),
    
)

t_expense_claim = Table(
    'expense_claim', metadata,
    Column('expense_claim_id', String(256)),
    Column('status', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('total', Numeric(18, 6)),
    Column('amount_due', Numeric(18, 6)),
    Column('amount_paid', Numeric(18, 6)),
    Column('payment_due_date', Date),
    Column('reporting_date', Date),
    Column('user_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('expense_claim_id', name='expense_claim_pkey'),
    
)

t_invoice = Table(
    'invoice', metadata,
    Column('invoice_id', String(128)),
    Column('type', String(256)),
    Column('invoice_number', String(256)),
    Column('reference', String(256)),
    Column('has_errors', Boolean),
    Column('is_discounted', Boolean),
    Column('has_attachments', Boolean),
    Column('line_amount_types', String(256)),
    Column('amount_due', Numeric(18, 6)),
    Column('amount_paid', Numeric(18, 6)),
    Column('amount_credited', Numeric(18, 6)),
    Column('currency_rate', Numeric(18, 6)),
    Column('cisdeduction', Numeric(18, 6)),
    Column('date', Date),
    Column('due_date', Date),
    Column('updated_date_utc', DateTime(True)),
    Column('fully_paid_on_date', Date),
    Column('currency_code', String(256)),
    Column('status', String(256)),
    Column('sub_total', Numeric(18, 6)),
    Column('total_tax', Numeric(18, 6)),
    Column('total', Numeric(18, 6)),
    Column('branding_theme_id', String(256)),
    Column('sent_to_contact', Boolean),
    Column('url', String(256)),
    Column('planned_payment_date', DateTime(True)),
    Column('expected_payment_date', DateTime(True)),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('invoice_id', name='invoice_pkey'),
    
)

t_invoice_line_item = Table(
    'invoice_line_item', metadata,
    Column('invoice_id', String(128), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('description', String(512)),
    Column('unit_amount', Numeric(18, 6)),
    Column('tax_type', String(256)),
    Column('tax_amount', Numeric(18, 6)),
    Column('line_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('item_code', String(256)),
    Column('discount_entered_as_percent', Boolean),
    Column('quantity', Numeric(18, 2)),
    Column('validation_errors', JSONB),
    Column('discount_rate', Integer),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('invoice_id', 'line_item_id', name='invoice_line_item_pkey'),
    
)

t_invoice_line_item_has_tracking_category = Table(
    'invoice_line_item_has_tracking_category', metadata,
    Column('invoice_id', String(256), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('tracking_category_id', String(256), nullable=False),
    Column('option', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('invoice_id', 'line_item_id', 'tracking_category_id', name='invoice_line_item_has_tracking_category_pkey'),
    
)

t_item = Table(
    'item', metadata,
    Column('item_id', String(256)),
    Column('code', String(256)),
    Column('description', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('purchase_description', String(256)),
    Column('purchase_details_unit_price', Numeric(18, 6)),
    Column('purchase_details_account_code', String(256)),
    Column('purchase_details_cogsaccount_code', String(256)),
    Column('purchase_details_tax_type', String(256)),
    Column('sales_details_unit_price', Numeric(18, 6)),
    Column('sales_details_account_code', String(256)),
    Column('sales_details_cogsaccount_code', String(256)),
    Column('sales_details_tax_type', String(256)),
    Column('name', String(256)),
    Column('is_tracked_as_inventory', Boolean),
    Column('is_sold', Boolean),
    Column('is_purchased', Boolean),
    Column('inventory_asset_account_code', String(256)),
    Column('total_cost_pool', Numeric(18, 6)),
    Column('quantity_on_hand', Numeric(18, 4)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('item_id', name='item_pkey'),
    
)

t_journal = Table(
    'journal', metadata,
    Column('journal_id', String(256)),
    Column('journal_date', Date),
    Column('journal_number', Integer),
    Column('created_date_utc', DateTime(True)),
    Column('reference', String(256)),
    Column('source_id', String(256)),
    Column('source_type', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('journal_id', name='journal_pkey'),
    
)

t_journal_line = Table(
    'journal_line', metadata,
    Column('journal_line_id', String(256)),
    Column('account_id', String(256)),
    Column('account_code', String(256)),
    Column('account_type', String(256)),
    Column('account_name', String(256)),
    Column('description', String(512)),
    Column('tax_type', String(256)),
    Column('tax_name', String(256)),
    Column('net_amount', Numeric(18, 6)),
    Column('gross_amount', Numeric(18, 6)),
    Column('tax_amount', Numeric(18, 6)),
    Column('journal_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('journal_line_id', name='journal_line_pkey'),
    
)

t_journal_line_has_tracking_category = Table(
    'journal_line_has_tracking_category', metadata,
    Column('journal_id', String(256), nullable=False),
    Column('journal_line_id', String(256), nullable=False),
    Column('tracking_category_id', String(256), nullable=False),
    Column('tracking_category_option_id', String(256)),
    Column('option', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('journal_id', 'journal_line_id', 'tracking_category_id', name='journal_line_has_tracking_category_pkey'),
    
)

t_manual_journal = Table(
    'manual_journal', metadata,
    Column('manual_journal_id', String(256)),
    Column('status', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('date', Date),
    Column('line_amount_types', String(256)),
    Column('narration', String(256)),
    Column('show_on_cash_basis_reports', Boolean),
    Column('has_attachments', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('manual_journal_id', name='manual_journal_pkey'),
    
)

t_manual_journal_line = Table(
    'manual_journal_line', metadata,
    Column('manual_journal_id', String(256), nullable=False),
    Column('line', Integer, nullable=False),
    Column('account_id', String(256)),
    Column('account_code', String(256)),
    Column('description', String(256)),
    Column('tax_type', String(256)),
    Column('is_blank', Boolean),
    Column('tax_amount', Numeric(18, 6)),
    Column('line_amount', Numeric(18, 6)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('manual_journal_id', 'line', name='manual_journal_line_pkey'),
    
)

t_organization = Table(
    'organization', metadata,
    Column('organisation_id', String(256)),
    Column('name', String(256)),
    Column('legal_name', String(256)),
    Column('apikey', String(256)),
    Column('version', String(256)),
    Column('organisation_type', String(256)),
    Column('line_of_business', String(256)),
    Column('base_currency', String(256)),
    Column('country_code', String(256)),
    Column('is_demo_company', Boolean),
    Column('organisation_status', String(256)),
    Column('tax_number', String(256)),
    Column('tax_number_name', String(256)),
    Column('financial_year_end_day', Integer),
    Column('financial_year_end_month', Integer),
    Column('sales_tax_basis', String(256)),
    Column('sales_tax_period', String(256)),
    Column('default_sales_tax', String(256)),
    Column('default_purchases_tax', String(256)),
    Column('pays_tax', Boolean),
    Column('period_lock_date', Date),
    Column('end_of_year_lock_date', Date),
    Column('created_date_utc', DateTime(True)),
    Column('organisation_entity_type', String(256)),
    Column('timezone', String(256)),
    Column('short_code', String(256)),
    Column('edition', String(256)),
    Column('registration_number', String(256)),
    Column('employer_identification_number', String(256)),
    Column('class', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('organisation_id', name='organization_pkey'),
    
)

t_payment = Table(
    'payment', metadata,
    Column('payment_id', String(256)),
    Column('date', Date),
    Column('bank_amount', Numeric(18, 6)),
    Column('amount', Numeric(18, 6)),
    Column('reference', String(256)),
    Column('currency_rate', Numeric(18, 6)),
    Column('payment_type', String(256)),
    Column('status', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('has_account', Boolean),
    Column('is_reconciled', Boolean),
    Column('batch_payment_date', DateTime(True)),
    Column('batch_payment_type', String(256)),
    Column('batch_payment_status', String(256)),
    Column('batch_payment_total_amount', Double(53)),
    Column('batch_payment_updated_date_utc', DateTime(True)),
    Column('batch_payment_is_reconciled', Boolean),
    Column('batch_payment_id', String(256)),
    Column('has_validation_errors', Boolean),
    Column('expense_claim_id', String(256)),
    Column('credit_note_id', String(256)),
    Column('overpayment_id', String(256)),
    Column('prepayment_id', String(256)),
    Column('account_id', String(256)),
    Column('invoice_id', String(128)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('payment_id', name='payment_pkey'),
    
)

t_purchase_order = Table(
    'purchase_order', metadata,
    Column('purchase_order_id', String(256)),
    Column('purchase_order_number', String(256)),
    Column('date', DateTime(True)),
    Column('delivery_date', DateTime(True)),
    Column('delivery_address', String(256)),
    Column('attention_to', String(256)),
    Column('telephone', String(256)),
    Column('delivery_instructions', String(256)),
    Column('is_discounted', Boolean),
    Column('reference', String(256)),
    Column('type', String(256)),
    Column('currency_rate', Double(53)),
    Column('currency_code', String(256)),
    Column('branding_theme_id', String(256)),
    Column('status', String(256)),
    Column('line_amount_types', String(256)),
    Column('sub_total', Double(53)),
    Column('total_tax', Double(53)),
    Column('total', Double(53)),
    Column('updated_date_utc', DateTime(True)),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('purchase_order_id', name='purchase_order_pkey'),
    
)

t_purchase_order_line_item = Table(
    'purchase_order_line_item', metadata,
    Column('purchase_order_id', String(256), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('description', String(256)),
    Column('item_code', String(256)),
    Column('quantity', Numeric(18, 2)),
    Column('unit_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('tax_type', String(256)),
    Column('line_amount', Numeric(18, 6)),
    Column('tax_amount', Numeric(18, 6)),
    Column('discount_rate', Numeric(18, 6)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('purchase_order_id', 'line_item_id', name='purchase_order_line_item_pkey'),
    
)

t_receipt = Table(
    'receipt', metadata,
    Column('receipt_id', String(256)),
    Column('receipt_number', Integer),
    Column('status', String(256)),
    Column('date', Date),
    Column('updated_date_utc', DateTime(True)),
    Column('reference', String(256)),
    Column('line_amount_types', String(256)),
    Column('sub_total', Numeric(18, 6)),
    Column('total_tax', Numeric(18, 6)),
    Column('total', Numeric(18, 6)),
    Column('id', String(256)),
    Column('has_attachments', Boolean),
    Column('expense_claim_id', String(256)),
    Column('user_id', String(256)),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('receipt_id', name='receipt_pkey'),
    
)

t_receipt_line_item = Table(
    'receipt_line_item', metadata,
    Column('receipt_id', String(256), nullable=False),
    Column('line', Integer, nullable=False),
    Column('description', String(256)),
    Column('quantity', Numeric(18, 2)),
    Column('unit_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('tax_type', String(256)),
    Column('line_amount', Numeric(18, 6)),
    Column('tax_amount', Numeric(18, 6)),
    Column('discount_entered_as_percent', Boolean),
    Column('discount_rate', Numeric(18, 6)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('receipt_id', 'line', name='receipt_line_item_pkey'),
    
)

t_receipt_line_item_has_tracking_category = Table(
    'receipt_line_item_has_tracking_category', metadata,
    Column('line', Integer, nullable=False),
    Column('receipt_id', String(256), nullable=False),
    Column('tracking_category_id', String(256), nullable=False),
    Column('tracking_category_option_id', String(256)),
    Column('option', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('line', 'receipt_id', 'tracking_category_id', name='receipt_line_item_has_tracking_category_pkey'),
    
)

t_repeating_invoice = Table(
    'repeating_invoice', metadata,
    Column('repeating_invoice_id', String(256)),
    Column('schedule_period', Numeric(18, 2)),
    Column('schedule_unit', String(256)),
    Column('schedule_due_date', Numeric(18, 2)),
    Column('schedule_due_date_type', String(256)),
    Column('schedule_start_date', Date),
    Column('schedule_next_scheduled_date', Date),
    Column('schedule_end_date', Date),
    Column('id', String(256)),
    Column('type', String(256)),
    Column('reference', String(256)),
    Column('has_attachments', Boolean),
    Column('status', String(256)),
    Column('line_amount_types', String(256)),
    Column('sub_total', Numeric(18, 6)),
    Column('total_tax', Numeric(18, 6)),
    Column('total_discount', Numeric(18, 6)),
    Column('total', Numeric(18, 6)),
    Column('currency_code', String(256)),
    Column('branding_theme_id', String(256)),
    Column('contact_id', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('repeating_invoice_id', name='repeating_invoice_pkey'),
    
)

t_repeating_invoice_line_item = Table(
    'repeating_invoice_line_item', metadata,
    Column('repeating_invoice_id', String(256), nullable=False),
    Column('line_item_id', String(256), nullable=False),
    Column('description', String(256)),
    Column('unit_amount', Numeric(18, 6)),
    Column('tax_type', String(256)),
    Column('tax_amount', Numeric(18, 6)),
    Column('line_amount', Numeric(18, 6)),
    Column('account_code', String(256)),
    Column('item_code', String(256)),
    Column('discount_entered_as_percent', Boolean),
    Column('quantity', Numeric(18, 2)),
    Column('validation_errors', JSONB),
    Column('discount_rate', Numeric(18, 6)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('repeating_invoice_id', 'line_item_id', name='repeating_invoice_line_item_pkey'),
    
)

t_settings = Table(
    'settings', metadata,
    Column('asset_number_sequence', String(256)),
    Column('asset_start_date', DateTime(True)),
    Column('last_depreciation_date', DateTime(True)),
    Column('default_gain_on_disposal_account_id', String(256)),
    Column('default_loss_on_disposal_account_id', String(256)),
    Column('default_capital_gain_on_disposal_account_id', String(256)),
    Column('opt_in_for_tax', Boolean),
    Column('asset_number_prefix', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('asset_number_sequence', name='settings_pkey'),
    
)

t_tax_rate = Table(
    'tax_rate', metadata,
    Column('_fivetran_id', String(256)),
    Column('name', String(256)),
    Column('tax_type', String(256)),
    Column('report_tax_type', String(256)),
    Column('can_apply_to_assets', Boolean),
    Column('can_apply_to_equity', Boolean),
    Column('can_apply_to_expenses', Boolean),
    Column('can_apply_to_liabilities', Boolean),
    Column('can_apply_to_revenue', Boolean),
    Column('display_tax_rate', Numeric(18, 6)),
    Column('effective_rate', Numeric(18, 6)),
    Column('status', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('_fivetran_id', name='tax_rate_pkey'),
    
)

t_tax_rate_component = Table(
    'tax_rate_component', metadata,
    Column('_fivetran_id', String(256), nullable=False),
    Column('name', String(256), nullable=False),
    Column('rate', Numeric(18, 6)),
    Column('is_compound', Boolean),
    Column('is_non_recoverable', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('_fivetran_id', 'name', name='tax_rate_component_pkey'),
    
)

t_tracking_category = Table(
    'tracking_category', metadata,
    Column('tracking_category_id', String(256)),
    Column('name', String(256)),
    Column('status', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('tracking_category_id', name='tracking_category_pkey'),
    
)

t_tracking_category_has_option = Table(
    'tracking_category_has_option', metadata,
    Column('tracking_category_id', String(256), nullable=False),
    Column('tracking_option_id', String(256), nullable=False),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('tracking_category_id', 'tracking_option_id', name='tracking_category_has_option_pkey'),
    
)

t_tracking_category_option = Table(
    'tracking_category_option', metadata,
    Column('tracking_option_id', String(256)),
    Column('name', String(256)),
    Column('status', String(256)),
    Column('has_validation_errors', Boolean),
    Column('is_deleted', Boolean),
    Column('is_archived', Boolean),
    Column('is_active', Boolean),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('tracking_option_id', name='tracking_category_option_pkey'),
    
)

t_user = Table(
    'user', metadata,
    Column('user_id', String(256)),
    Column('email_address', String(256)),
    Column('first_name', String(256)),
    Column('last_name', String(256)),
    Column('updated_date_utc', DateTime(True)),
    Column('is_subscriber', Boolean),
    Column('organisation_role', String(256)),
    Column('_fivetran_synced', DateTime(True)),
    PrimaryKeyConstraint('user_id', name='user_pkey'),
    
)
