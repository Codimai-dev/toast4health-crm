"""Finance forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField, SelectField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class SaleForm(FlaskForm):
    """Form for adding/editing sales."""

    invoice_number = StringField('Invoice Number', validators=[DataRequired()],
                                render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    date = DateField('Date', validators=[DataRequired()],
                    render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    customer_name = SelectField('Customer Name', choices=[('', 'Select Customer or Enter New')], validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'autocomplete': 'off'})
    customer_name_new = StringField('Or Enter New Customer Name', validators=[Optional()],
                                   render_kw={'class': 'form-control', 'placeholder': 'Enter new customer name', 'autocomplete': 'off'})
    product_service = StringField('Product/Service', validators=[DataRequired()],
                                 render_kw={'class': 'form-control', 'placeholder': 'Describe product or service', 'autocomplete': 'off'})
    
    # GST fields
    base_amount = DecimalField('Amount (₹)', validators=[DataRequired(), NumberRange(min=0)],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off', 'id': 'base_amount'})
    gst_type = SelectField('GST Type', 
                          choices=[('exclusive', 'Exclusive'), ('inclusive', 'Inclusive')],
                          validators=[DataRequired()], default='exclusive',
                          render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'gst_type'})
    gst_percentage = IntegerField('GST %', validators=[DataRequired(), NumberRange(min=0, max=100)],
                                 default=18,
                                 render_kw={'class': 'form-control', 'placeholder': '18', 'autocomplete': 'off', 'id': 'gst_percentage'})
    gst_amount = DecimalField('GST Amount (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'gst_amount'})
    amount = DecimalField('Total Amount (₹)', validators=[Optional()],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'total_amount'})
    
    payment_status = SelectField('Payment Status', 
                                choices=[('Pending', 'Pending'), ('Received', 'Received'), ('Partial', 'Partial')],
                                validators=[DataRequired()], default='Pending',
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    notes = TextAreaField('Notes', validators=[Optional()],
                         render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes', 'autocomplete': 'off'})
    
    # Payment fields (shown only when payment_status is Received or Partial)
    payment_amount = DecimalField('Payment Amount (₹)', validators=[Optional(), NumberRange(min=0)],
                                 places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off'})
    payment_date = DateField('Payment Date', validators=[Optional()],
                            render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    payment_method = SelectField('Payment Method', 
                                choices=[('', 'Select Payment Method'), ('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), 
                                        ('Cheque', 'Cheque'), ('UPI', 'UPI'), ('Card', 'Card'), ('Other', 'Other')],
                                validators=[Optional()],
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    payment_remarks = TextAreaField('Payment Remarks', validators=[Optional()],
                                   render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional payment remarks', 'autocomplete': 'off'})
    
    submit = SubmitField('Save Sale', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate customer choices from both Customer table and converted B2C leads
        from app.models import Customer, B2CLead
        
        # Get actual customers
        customers = Customer.query.order_by(Customer.customer_name).all()
        
        # Get converted B2C leads that are not yet customers
        converted_leads = B2CLead.query.filter_by(status='converted').order_by(B2CLead.customer_name).all()
        
        # Build choices list
        choices = [('', 'Select Customer or Enter New')]
        
        # Add actual customers
        for c in customers:
            choices.append((c.customer_name, f"{c.customer_name} ({c.customer_code})"))
        
        # Add converted leads
        for l in converted_leads:
            choices.append((l.customer_name, f"{l.customer_name} ({l.enquiry_id} - Converted Lead)"))
        
        self.customer_name.choices = choices


class PurchaseForm(FlaskForm):
    """Form for adding/editing purchases."""

    bill_number = StringField('Bill Number', validators=[DataRequired()],
                             render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    date = DateField('Date', validators=[DataRequired()],
                    render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    vendor_name = StringField('Vendor Name', validators=[DataRequired()],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter vendor name', 'autocomplete': 'off'})
    item_description = StringField('Item/Description', validators=[DataRequired()],
                                  render_kw={'class': 'form-control', 'placeholder': 'Describe item or service', 'autocomplete': 'off'})
    
    # GST fields
    base_amount = DecimalField('Amount (₹)', validators=[DataRequired(), NumberRange(min=0)],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off', 'id': 'base_amount'})
    gst_type = SelectField('GST Type', 
                          choices=[('exclusive', 'Exclusive'), ('inclusive', 'Inclusive')],
                          validators=[DataRequired()], default='exclusive',
                          render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'gst_type'})
    gst_percentage = IntegerField('GST %', validators=[DataRequired(), NumberRange(min=0, max=100)],
                                 default=18,
                                 render_kw={'class': 'form-control', 'placeholder': '18', 'autocomplete': 'off', 'id': 'gst_percentage'})
    gst_amount = DecimalField('GST Amount (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'gst_amount'})
    amount = DecimalField('Total Amount (₹)', validators=[Optional()],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'total_amount'})
    
    payment_status = SelectField('Payment Status', 
                                choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Partial', 'Partial')],
                                validators=[DataRequired()], default='Pending',
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    notes = TextAreaField('Notes', validators=[Optional()],
                         render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes', 'autocomplete': 'off'})
    
    # Payment fields (shown only when payment_status is Paid or Partial)
    payment_amount = DecimalField('Payment Amount (₹)', validators=[Optional(), NumberRange(min=0)],
                                 places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off'})
    payment_date = DateField('Payment Date', validators=[Optional()],
                            render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    payment_method = SelectField('Payment Method', 
                                choices=[('', 'Select Payment Method'), ('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), 
                                        ('Cheque', 'Cheque'), ('UPI', 'UPI'), ('Card', 'Card'), ('Other', 'Other')],
                                validators=[Optional()],
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    payment_remarks = TextAreaField('Payment Remarks', validators=[Optional()],
                                   render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional payment remarks', 'autocomplete': 'off'})
    
    submit = SubmitField('Save Purchase', render_kw={'class': 'btn btn-primary'})


class PaymentReceivedForm(FlaskForm):
    """Form for adding/editing payments received."""

    reference_number = StringField('Reference Number', validators=[DataRequired()],
                                  render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    date = DateField('Date', validators=[DataRequired()],
                    render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    customer_name = SelectField('Customer Name', choices=[('', 'Select Customer or Enter New')], validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'autocomplete': 'off'})
    customer_name_new = StringField('Or Enter New Customer Name', validators=[Optional()],
                                   render_kw={'class': 'form-control', 'placeholder': 'Enter new customer name', 'autocomplete': 'off'})
    amount = DecimalField('Gross Amount (₹)', validators=[DataRequired(), NumberRange(min=0)],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off', 'id': 'gross_amount'})
    
    # TDS fields
    tds_applicable = SelectField('TDS Applicable', 
                                choices=[('no', 'No'), ('yes', 'Yes')],
                                validators=[DataRequired()], default='no',
                                render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'tds_applicable'})
    tds_section = SelectField('TDS Section', 
                             choices=[('', 'Select Section'), ('194C', '194C - Contractors'), ('194J', '194J - Professional Services'), 
                                     ('194H', '194H - Commission'), ('194I', '194I - Rent'), ('194A', '194A - Interest'), ('Other', 'Other')],
                             validators=[Optional()],
                             render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'tds_section'})
    tds_percentage = DecimalField('TDS %', validators=[Optional(), NumberRange(min=0, max=100)],
                                 places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'autocomplete': 'off', 'id': 'tds_percentage'})
    tds_amount = DecimalField('TDS Amount (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'tds_amount'})
    net_amount = DecimalField('Net Amount (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'net_amount'})
    
    payment_method = SelectField('Payment Method', 
                                choices=[('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), 
                                        ('Cheque', 'Cheque'), ('UPI', 'UPI'), ('Card', 'Card'), ('Other', 'Other')],
                                validators=[DataRequired()], default='Cash',
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    invoice_number = SelectField('Related Invoice', choices=[('', 'Select Invoice (Optional)')], validators=[Optional()],
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    remarks = TextAreaField('Remarks', validators=[Optional()],
                           render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks', 'autocomplete': 'off'})
    submit = SubmitField('Save Payment', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate customer choices from both Customer table and converted B2C leads
        from app.models import Customer, Sale, B2CLead
        
        # Get actual customers
        customers = Customer.query.order_by(Customer.customer_name).all()
        
        # Get converted B2C leads that are not yet customers
        converted_leads = B2CLead.query.filter_by(status='converted').order_by(B2CLead.customer_name).all()
        
        # Build choices list
        choices = [('', 'Select Customer or Enter New')]
        
        # Add actual customers
        for c in customers:
            choices.append((c.customer_name, f"{c.customer_name} ({c.customer_code})"))
        
        # Add converted leads
        for l in converted_leads:
            choices.append((l.customer_name, f"{l.customer_name} ({l.enquiry_id} - Converted Lead)"))
        
        self.customer_name.choices = choices
        
        # Populate invoice choices
        sales = Sale.query.order_by(Sale.date.desc()).all()
        self.invoice_number.choices = [('', 'Select Invoice (Optional)')] + \
                                     [(s.invoice_number, f"{s.invoice_number} - {s.customer_name}") for s in sales]


class PaymentMadeForm(FlaskForm):
    """Form for adding/editing payments made."""

    reference_number = StringField('Reference Number', validators=[DataRequired()],
                                  render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    date = DateField('Date', validators=[DataRequired()],
                    render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    payee_name = StringField('Payee Name', validators=[DataRequired()],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter payee name', 'autocomplete': 'off'})
    amount = DecimalField('Gross Amount (₹)', validators=[DataRequired(), NumberRange(min=0)],
                         places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'autocomplete': 'off', 'id': 'gross_amount_made'})
    
    # TDS fields
    tds_applicable = SelectField('TDS Applicable', 
                                choices=[('no', 'No'), ('yes', 'Yes')],
                                validators=[DataRequired()], default='no',
                                render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'tds_applicable_made'})
    tds_section = SelectField('TDS Section', 
                             choices=[('', 'Select Section'), ('194C', '194C - Contractors'), ('194J', '194J - Professional Services'), 
                                     ('194H', '194H - Commission'), ('194I', '194I - Rent'), ('194A', '194A - Interest'), ('Other', 'Other')],
                             validators=[Optional()],
                             render_kw={'class': 'form-control', 'autocomplete': 'off', 'id': 'tds_section_made'})
    tds_percentage = DecimalField('TDS %', validators=[Optional(), NumberRange(min=0, max=100)],
                                 places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'autocomplete': 'off', 'id': 'tds_percentage_made'})
    tds_amount = DecimalField('TDS Amount (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'tds_amount_made'})
    net_amount = DecimalField('Net Amount Paid (₹)', validators=[Optional()],
                             places=2, render_kw={'class': 'form-control', 'placeholder': '0.00', 'readonly': True, 'autocomplete': 'off', 'id': 'net_amount_made'})
    
    payment_method = SelectField('Payment Method', 
                                choices=[('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), 
                                        ('Cheque', 'Cheque'), ('UPI', 'UPI'), ('Card', 'Card'), ('Other', 'Other')],
                                validators=[DataRequired()], default='Cash',
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    category = SelectField('Category', 
                          choices=[('Purchases', 'Purchases'), ('Office Rent', 'Office Rent'), 
                                  ('Utilities', 'Utilities'), ('Salary', 'Salary'), 
                                  ('Marketing', 'Marketing'), ('Miscellaneous', 'Miscellaneous')],
                          validators=[DataRequired()],
                          render_kw={'class': 'form-control', 'autocomplete': 'off'})
    bill_number = SelectField('Related Bill', choices=[('', 'Select Bill (Optional)')], validators=[Optional()],
                             render_kw={'class': 'form-control', 'autocomplete': 'off'})
    remarks = TextAreaField('Remarks', validators=[Optional()],
                           render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks', 'autocomplete': 'off'})
    submit = SubmitField('Save Payment', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate bill choices
        from app.models import Purchase
        purchases = Purchase.query.order_by(Purchase.date.desc()).all()
        self.bill_number.choices = [('', 'Select Bill (Optional)')] + \
                                   [(p.bill_number, f"{p.bill_number} - {p.vendor_name}") for p in purchases]


class ChartOfAccountForm(FlaskForm):
    """Form for adding/editing chart of accounts."""

    account_code = IntegerField('Account Code', validators=[DataRequired(), NumberRange(min=1000, max=9999)],
                               render_kw={'class': 'form-control', 'placeholder': 'e.g., 1000', 'autocomplete': 'off'})
    account_name = StringField('Account Name', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter account name', 'autocomplete': 'off'})
    account_type = SelectField('Account Type', 
                              choices=[('Asset', 'Asset'), ('Liability', 'Liability'), 
                                      ('Equity', 'Equity'), ('Income', 'Income'), ('Expense', 'Expense')],
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'autocomplete': 'off'})
    description = TextAreaField('Description', validators=[Optional()],
                               render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description', 'autocomplete': 'off'})
    submit = SubmitField('Save Account', render_kw={'class': 'btn btn-primary'})
