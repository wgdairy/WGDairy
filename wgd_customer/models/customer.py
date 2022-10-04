from odoo import fields, models, api #, re
import re
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import date, datetime

class Customer(models.Model):
    '''
        Inherit partner module to create a new customized customer module
    '''
    _name = 'my.customer'
    _inherits = {'res.partner': 'partner_id'}
    # _order = "name asc"
    # _columns = {
    #     'partner_id': fields.Many2one('my.customer', 'Partner Details', help="Link this vendor to it's partner",
    #                                   ondelete="cascade", required=True),
    # }

    def _get_default_country(self):

        country = self.env['res.country'].search([('code', '=', 'US')], limit=1)

        return country
    
    customer_id             = fields.Char("Customer ID",help='Exportable')
    # partner_id              = fields.Many2one('res.partner')    
    job_id                  = fields.Selection([('0','0'),('1','1'),('2','2')], "Store", default='1',help='Exportable')
    has_job                 = fields.Selection([('Y','Y'),('N','N')], "Has Job?",help='Exportable')
    # sort_name_id            = fields.Many2one('sort')
    sort_name_id            = fields.Char("Sort",help='Exportable')
    bill_to_id              = fields.Many2one('res.partner')
    ace_rewards             = fields.Char("Ace Rewards",help='Exportable')
    filter_by_name          = fields.Many2one('my.customer')
    filter_by_id            = fields.Many2one('my.customer')

    # notebook page1 Main
    phone                   = fields.Char('Phone',help='Exportable')
    fax                     = fields.Char('Fax',help='Exportable')
    contact                 = fields.Char('Contact',help='Exportable')
    country_id              = fields.Many2one('res.country', string='Country',default=_get_default_country)
    credit_message1         = fields.Char(' ',help='Exportable')
    credit_message2         = fields.Char(' ',help='Exportable')

    credit_limit            = fields.Float("Credit Limit")
    trade_discount          = fields.Float('Trade Discount %',help='Exportable',size=4)
    account_code1           = fields.Char('account_code1',help='Exportable')
    monthly_payment         = fields.Integer('Monthly Payment',help='Exportable')
    # category_plan           = fields.Many2one("", string='Category Plan', ondelete='restrict',help='Exportable')
    # tax_code                = fields.Many2one("", string='Tax Code', ondelete='restrict',help='Exportable')
    # salesperson             = fields.Many2one("", string='Salesperson', ondelete='restrict',help='Exportable')
    # terms_code              = fields.Many2one("", string='Terms Code', ondelete='restrict',help='Exportable')
    terms_code              = fields.Many2one('account.payment.term', 'Terms Code')

    category_plan_id        = fields.Many2one('category')
    tax_code                = fields.Selection([('yes','Y'),('no','N')], "Tax Code", default='yes',help='Exportable')
    salesperson             = fields.Selection([('yes','Y'),('no','N')], "Salesperson", default='no',help='Exportable')
    # terms_code              = fields.Selection([('yes','Y'),('no','N')], "Terms Code", default='no')
    pure_archive_invoices   = fields.Char('Pure Archive Invoices',help='Exportable')

    po_required             = fields.Selection([('yes','Y'),('no','N')], "PO Required", default='no',help='Exportable')
    default_po              = fields.Char('Default PO',help='Exportable')
    
    # balance_method          = fields.Selection([('yes','0'),('no','0')], "Balance Method", default='no')
    charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed", default='yes',help='Exportable')
    balance_method          = fields.Many2one('balance',default=lambda self: self.env['balance'].search([('name','=','O')]), limit=1)

    std_sell_price          = fields.Selection([('yes','R'),('no','R')], "Std Sell Price/POS", default='no',help='Exportable')
    finace_charges          = fields.Monetary(string="Finace Charges")
    store_acct_opened_id    = fields.Many2one('res.company')
    transfer_to_store       = fields.Selection([('yes','Y'),('no','N')], "Transfer To Store", default='no',help='Exportable')
    print_statments         = fields.Selection([('yes','Y'),('no','N')], "Print Statments", default='no')
    # charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed", default='yes',help='Exportable')
    check_allowed           = fields.Selection([('yes','Y'),('no','N')], "Check Allowed", default='no',help='Exportable')
    credit_are_only         = fields.Selection([('yes','Y'),('no','N')], "Credit A/R Only", default='no',help='Exportable')
    taxable                 = fields.Selection([('yes','Y'),('no','N')], "Taxable", default='no')
    keep_dept_history       = fields.Selection([('yes','Y'),('no','N')], "Keep Dept History", default='yes',help='Exportable')
    print_invoices_in_pos   = fields.Selection([('yes','Y'),('no','N')], "Print Invoices In POS", default='no',help='Exportable')
    last_activity_date      = fields.Date("Last Activity Date")


# notebook page2 Credit
    finace_chgs_ytd         = fields.Float("Finace Chgs YTD", digits=(2,2))
    #credit_limit_2          = fields.Integer("Credit Limit")
    higest_acc_balance      = fields.Float("Higest Acct Balance")
    credit_available        = fields.Float("Credit Available",compute="_total_credit") 
    running_balance         = fields.Float("Running Balance",compute="_total_running_bal")
    statment_balance        = fields.Float("Statment Balance",compute="_total_stmt_bal")
    statment_discount       = fields.Float("Statment Discount")
    returns                 = fields.Float("Returns",compute="_total_refund")
    transations             = fields.Float("Transations",compute="_total_invoices")

    # check_allowed           = fields.Selection([('yes','Y'),('no','N')], "Check Allowed", default='no',help='Exportable')
    # credit_are_only         = fields.Selection([('yes','Y'),('no','N')], "Credit Are Only", default='no',help='Exportable')
    # taxable                 = fields.Selection([('yes','Y'),('no','N')], "Taxable", default='no')
    # keep_dept_history       = fields.Selection([('yes','Y'),('no','N')], "Keep Dept History", default='yes',help='Exportable')
    declining_credit_limit  = fields.Selection([('yes','Y'),('no','N')], "Declining Credit Limit", default='yes',help='Exportable')
    global_credit_check     = fields.Selection([('yes','Y'),('no','N')], "Global Credit Check", default='no',help='Exportable')
    order_bal_credit_avail  = fields.Selection([('yes','Y'),('no','N')], "Use Order Bal in Credit Avail", default='no',help='Exportable')
    
    last_sale               = fields.Date("Last Sale")
    acct_opened             = fields.Date("Acct Opened")

    # balance_method          = fields.Selection([('yes','Y'),('no','N')], "Balance Method", default='no')
    # charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed ?", default='yes',help='Exportable')
    # store_acct_opened       = fields.Selection([('yes','Y'),('no','N')], "StoreAcct Opened", default='yes',help='Exportable')
    # finace_charges          = fields.Selection([('yes','Y'),('no','N')], "Finace Charges", default='no')
    monthly_payment         = fields.Integer('Monthly Payment',help='Exportable')
    lyr_fin_charge          = fields.Float('LYR Fin Charge',help='Exportable')
    date_last_pay           = fields.Date("Date Last Pay")
    amount_last_pay         = fields.Monetary("Amount Last Pay")
    special_charges         = fields.Integer("Special Charges")


# notebook page3 Dept
    store                   = fields.Selection([('1','1'),('2','2')], "Store", default='1',help='Exportable')
    std_sell_prices         = fields.Integer("Std Sell Price")
    delete_all              = fields.Boolean(string = "Delete All Department History?")
    customer_sales_summary  = fields.Char('Customer Sales Summary',help='Exportable')

    credit_ids              = fields.One2many('credit', 'customer_ids',string=" ")  

    period_to_date_sale     = fields.Float("Sale")
    period_to_date_cost     = fields.Float("Cost")
    period_to_date_gp       = fields.Float("GP %")
    year_to_date_sale       = fields.Float("Sale")
    year_to_date_cost       = fields.Float("Cost")
    year_to_date_gp         = fields.Float("GP %")
    last_year_sale          = fields.Float("Sale")
    last_year_cost          = fields.Float("Cost")
    last_year_gp            = fields.Float("GP %")

# notebook page4 Sales
    
    # period_to_date_sale     = fields.Float("Sale")
    # period_to_date_cost     = fields.Float("Cost")
    # period_to_date_gp       = fields.Float("GP %")
    # year_to_date_sale       = fields.Float("Sale")
    # year_to_date_cost       = fields.Float("Cost")
    # year_to_date_gp         = fields.Float("GP %")
    # last_year_sale          = fields.Float("Sale")
    # last_year_cost          = fields.Float("Cost")
    # last_year_gp            = fields.Float("GP %")

    period_to_date_gp_dollor= fields.Float("GP $")
    year_to_date__dollor    = fields.Float("GP $")
    last_year_gp_dollor     = fields.Float("GP $")
    terms_disc              = fields.Float("Terms Disc")
    year_to_date_fin_chrgs  = fields.Float("Finance Charges")
    last_year_gp_fin_chrgs  = fields.Float("Finance Charges")
    year_to_date_returns    = fields.Float("Returns")
    year_to_date_transaction= fields.Float("Transations")
    customer_sales_summary  = fields.Float("Customer Sales Summary")


# notebook page5 Payment

    # higest_acc_balance      = fields.Float("Higest Acct Balance")
    # date_last_pay           = fields.Date("Date Last Pay")
    # amount_last_pay         = fields.Float("Amount Last Pay")
    # finace_charges          = fields.Selection([('yes','Y'),('no','N')], "Finace Charges", default='no')
    # monthly_payment         = fields.Integer('Monthly Payment',help='Exportable')
    # credit_limit            = fields.Float("Credit Limit")
    # running_balance         = fields.Float("Running Balance")
    # credit_available        = fields.Float("Credit Available")

    of_times_no_activity    = fields.Float("No Activity")
    of_times_current        = fields.Float("Current")
    of_times_1_30           = fields.Float("1 - 30")
    of_times_31_60          = fields.Float("31 - 60")
    of_times_61_90          = fields.Float("61 - 90")
    of_times_over_90        = fields.Float("Over 90")

    last_occured_no_activity= fields.Date("")
    last_occured_current    = fields.Date("")
    last_occured_1_30       = fields.Date("")
    last_occured_31_60      = fields.Date("")
    last_occured_61_90      = fields.Date("")
    last_occured_over_90    = fields.Date("")

    jan                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Jan", default='1-30',help='Exportable')
    feb                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Feb", default='1-30',help='Exportable')
    mar                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Mar", default='1-30',help='Exportable')
    apr                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Apr", default='1-30',help='Exportable')
    may                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "May", default='1-30',help='Exportable')
    jun                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Jun", default='1-30',help='Exportable')
    jul                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Jul", default='1-30',help='Exportable')
    aug                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Aug", default='1-30',help='Exportable')
    sep                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Sep", default='1-30',help='Exportable')
    octo                    = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Oct", default='1-30',help='Exportable')
    nov                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Nov", default='1-30',help='Exportable')
    dec                     = fields.Selection([('1-30','1-30'),('31-60','31-60'),('61-90','61-90'),('over_90','Over 90')], "Dec", default='1-30',help='Exportable')

# notebook page6 Names
    social_security         = fields.Char('Social Security',help='Exportable')
    birth_date              = fields.Date("Birth Date")
    pst_registration        = fields.Date('PST Regisration',help='Exportable')
    gst_registration        = fields.Date('GST Regisration',help='Exportable')
    pesticide_license       = fields.Date('Pesticide License',help='Exportable')
    pesticide_lic_exp       = fields.Date('Pesticide Lic. Exp.',help='Exportable')
    freght_factor           = fields.Float('Freght Factor',help='Exportable')
    rescale_code            = fields.Char('Rescale Code',help='Exportable')
    alternate_phone         = fields.Char('Alternative Phone',help='Exportable')
    alternate_fax           = fields.Char('Alternative Fax',help='Exportable')
    open_quote_1            = fields.Char('Open Quote Doc#/St',help='Exportable')
    open_quote_2            = fields.Char('',help='Exportable')
    rebate_plan             = fields.Selection([('1',' '),('2','2')], "Rebate Plan",help='Exportable')
    
    business_type           = fields.Selection([('1',' '),('2','2')], "Business Type",help='Exportable')
    location                = fields.Selection([('1',' '),('2','2')], "Location",help='Exportable')
    customer_ranks          = fields.Selection([('1',' '),('2','2')], "Customer Rank",help='Exportable')
    statment_type           = fields.Selection([('1',' '),('2','2')], "Statment Type",help='Exportable')

    statment_fmt            = fields.Selection([('1','Statement'),('2','Digital')], "Statment/Fmt",help='Exportable')
    statment_fmt2           = fields.Selection([('1','E'),('2','M')], "",help='Exportable')
    Invoice_credit          = fields.Selection([('1',' '),('2','2')], "Invoice/Credit",help='Exportable')
    order_sp_ord_estimate   = fields.Selection([('1',' '),('2','2')], "Order/Sp.Ord/Estimate",help='Exportable')

    fax_pos_stmt            = fields.Selection([('1',' '),('2','2')], "Fax POS/Stmt",help='Exportable')
    fax_pos_stmt1           = fields.Selection([('1',' '),('2','2')], "Fax POS/Stmt",help='Exportable')
    ace_rewards_status      = fields.Selection([('A','A'),('I','I'),('N','N')], "Ace Rewards Status",default='A',help='Exportable')
    tax_override_plan       = fields.Selection([('1',' '),('2','2')], "Tax Override Plan",help='Exportable')
    
    prompt_in_pos           = fields.Selection([('1',' '),('2','2')], "Prompt in POS?",help='Exportable')
    prompt_threshold        = fields.Char('Prompt Threshold',help='Exportable')
   
    price_pick_ticket       = fields.Selection([('y','Y'),('n','N')], "Price Pick Ticket", default='y',help='Exportable')
    open_quotes             = fields.Selection([('y','Y'),('n','N')], "Open Quote", default='n',help='Exportable')
    global_credit_check     = fields.Selection([('1',' '),('2','2')], "Global Credit Check",help='Exportable')
    print_lumber_totals     = fields.Selection([('y','Y'),('n','N')], "Print Lumber Totals", default='y',help='Exportable')
    # store_job_opened        = fields.Selection([('1','1'),('2','2')], "Store Job Opened", default='1',help='Exportable')
    # default_price_um        = fields.Selection([('1',' '),('2','2')], "Default Price UM",help='Exportable')
    default_price_uom       = fields.Many2one('uom.uom')

    statment_by_job         = fields.Selection([('s','S')], "Statment By Job", default='s',help='Exportable')

    additional_flag          = fields.Char('Additional Flags',help='Exportable')
    
    names_ids              = fields.One2many('names', 'customer_ids',string=" ") 

# notebook page8 Note
    types                   = fields.Selection([('1','1'),('2','2')], "Type", default='1',help='Exportable')
    display_repeat          = fields.Selection([('yes','Y'),('no','N')], "Display Repeats", default='yes',help='Exportable')
    print_repeat            = fields.Selection([('yes','Y'),('no','N')], "Print Repeats", default='no',help='Exportable')                 
    message                 = fields.Html("Message")

#smart button
    current_total           = fields.Float("Current",compute="_smart_button")  
    thirty_total            = fields.Float("Current",compute="_smart_button")  
    sixty_total             = fields.Float("Current",compute="_smart_button")  
    ninety_total            = fields.Float("Current",compute="_smart_button")  
    over_total              = fields.Float("Current",compute="_smart_button")  

    def action_student_schedules(self):
        pass
    
    @api.onchange('filter_by_name','filter_by_id')
    def onchange_name_and_id(self):
        if self.filter_by_name:
            customer_name = self.search([('name', '=', self.filter_by_name.name)])
            if customer_name:
                self.street= customer_name.street
                self.street2= customer_name.street2
                self.city= customer_name.city
                self.state_id= customer_name.state_id
                self.zip= customer_name.zip
                self.country_id= customer_name.country_id
                self.phone= customer_name.phone
                self.fax= customer_name.fax
                self.contact= customer_name.contact
                self.country_id= customer_name.country_id
                self.credit_message1= customer_name.credit_message1
                self.credit_message2= customer_name.credit_message2
                self.credit_limit= customer_name.credit_limit
                self.trade_discount= customer_name.trade_discount
                self.account_code1= customer_name.account_code1
                self.monthly_payment= customer_name.monthly_payment
                self.terms_code= customer_name.terms_code
                self.category_plan_id= customer_name.category_plan_id
                self.tax_code= customer_name.tax_code
                self.salesperson= customer_name.salesperson
                self.pure_archive_invoices= customer_name.pure_archive_invoices
                self.po_required= customer_name.po_required
                self.default_po= customer_name.default_po
                self.balance_method= customer_name.balance_method
                self.std_sell_price= customer_name.std_sell_price
                self.finace_charges= customer_name.finace_charges
                self.store_acct_opened_id= customer_name.store_acct_opened_id
                self.transfer_to_store= customer_name.transfer_to_store
                self.print_statments= customer_name.print_statments
                self.check_allowed= customer_name.check_allowed
                self.credit_are_only= customer_name.credit_are_only
                self.taxable= customer_name.taxable
                self.keep_dept_history= customer_name.keep_dept_history
                self.print_invoices_in_pos= customer_name.print_invoices_in_pos
                self.last_activity_date=customer_name.last_activity_date

                self.customer_id= customer_name.customer_id
                self.job_id= customer_name.job_id
                self.has_job= customer_name.has_job
                self.sort_name_id= customer_name.sort_name_id
                self.bill_to_id= customer_name.bill_to_id
                self.ace_rewards= customer_name.ace_rewards
                self.name= customer_name.name

               
        if self.filter_by_id:
            customer_id = self.search([('customer_id', '=', self.filter_by_id.customer_id)])
            if customer_id:
                self.street= customer_id.street
                self.street2= customer_id.street2
                self.city= customer_id.city
                self.state_id= customer_id.state_id
                self.zip= customer_id.zip
                self.country_id= customer_id.country_id
                self.phone= customer_id.phone
                self.fax= customer_id.fax
                self.contact= customer_id.contact
                self.country_id= customer_id.country_id
                self.credit_message1= customer_id.credit_message1
                self.credit_message2= customer_id.credit_message2
                self.credit_limit= customer_id.credit_limit
                self.trade_discount= customer_id.trade_discount
                self.account_code1= customer_id.account_code1
                self.monthly_payment= customer_id.monthly_payment
                self.terms_code= customer_id.terms_code
                self.category_plan_id= customer_id.category_plan_id
                self.tax_code= customer_id.tax_code
                self.salesperson= customer_id.salesperson
                self.pure_archive_invoices= customer_id.pure_archive_invoices
                self.po_required= customer_id.po_required
                self.default_po= customer_id.default_po
                self.balance_method= customer_id.balance_method
                self.std_sell_price= customer_id.std_sell_price
                self.finace_charges= customer_id.finace_charges
                self.store_acct_opened_id= customer_id.store_acct_opened_id
                self.transfer_to_store= customer_id.transfer_to_store
                self.print_statments= customer_id.print_statments
                self.check_allowed= customer_id.check_allowed
                self.credit_are_only= customer_id.credit_are_only
                self.taxable= customer_id.taxable
                self.keep_dept_history= customer_id.keep_dept_history
                self.print_invoices_in_pos= customer_id.print_invoices_in_pos
                self.last_activity_date=customer_id.last_activity_date    

                self.customer_id= customer_id.customer_id
                self.job_id= customer_id.job_id
                self.has_job= customer_id.has_job
                self.sort_name_id= customer_id.sort_name_id
                self.bill_to_id= customer_id.bill_to_id
                self.ace_rewards= customer_id.ace_rewards
                self.name= customer_id.name
    
    @api.depends('current_total','thirty_total','sixty_total','ninety_total','over_total')
    def _smart_button(self):
        '''
            Fetch invoice details from aged recivable 
        '''
        current_date    = date.today()
        customer_invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),('partner_id', '=', self.partner_id.id),('state', '=', 'posted'),('invoice_date', '<=', current_date)])
        refund__invoices  = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.partner_id.id),('state', '=', 'posted'),('invoice_date', '<=', current_date)])
        day = 0
        current_total1 = 0.0
        total_30 = 0.0 
        total_60 = 0.0
        total_90 = 0.0 
        over_90  = 0.0
        for record in customer_invoices:
            if record.invoice_date == current_date:
                if record.invoice_date_due == current_date or record.invoice_date_due > current_date:
                    current_total1 =  current_total1 + record.amount_residual
                else:
                    count = current_date - record.invoice_date_due
                    day = count.days
                    if day < 0:
                        day = day * -1
                    if day < 31:
                        total_30 = total_30 + record.amount_residual
                    elif day < 61:
                        total_60 = total_60 + record.amount_residual
                    elif day < 91:
                        total_90 = total_90 + record.amount_residual
                    else: 
                        over_90 = over_90 + record.amount_residual
            else:
                if record.invoice_date_due == current_date or record.invoice_date_due > current_date:
                    current_total1 =  current_total1 + record.amount_residual
                else:
                    count = current_date - record.invoice_date_due
                    day = count.days
                    if day < 0:
                        day = day * -1
                    if day < 31:
                        total_30 = total_30 + record.amount_residual
                    elif day < 61:
                        total_60 = total_60 + record.amount_residual
                    elif day < 91:
                        total_90 = total_90 + record.amount_residual
                    else: 
                        over_90 = over_90 + record.amount_residual

        for record in refund__invoices:
            if record.invoice_date == current_date:
                if record.invoice_date_due == current_date or record.invoice_date_due > current_date:
                    current_total1 =  current_total1 - record.amount_residual
                else:
                    count = current_date - record.invoice_date_due
                    day = count.days
                    if day < 0:
                        day = day * -1
                    if day < 31:
                        total_30 = total_30 - record.amount_residual
                    elif day < 61:
                        total_60 = total_60 - record.amount_residual
                    elif day < 91:
                        total_90 = total_90 - record.amount_residual
                    else: 
                        over_90 = over_90 - record.amount_residual
            else:
                if record.invoice_date_due == current_date or record.invoice_date_due > current_date:
                    current_total1 =  current_total1 - record.amount_residual
                else:
                    count = current_date - record.invoice_date_due
                    day = count.days
                    if day < 0:
                        day = day * -1
                    if day < 31:
                        total_30 = total_30 - record.amount_residual
                    elif day < 61:
                        total_60 = total_60 - record.amount_residual
                    elif day < 91:
                        total_90 = total_90 - record.amount_residual
                    else: 
                        over_90 = over_90 - record.amount_residual            
        self.current_total = current_total1
        self.thirty_total  = total_30
        self.sixty_total   = total_60
        self.ninety_total  = total_90
        self.over_total    = over_90


    def validate_float(self, float_value, val):
        if float_value:
            if val == "Period GP %" or val == "Last Year GP":
                if len(str(float_value)) > 6:
                    raise ValidationError("4 digits be allowed in %s" % val)
            elif len(str(float_value)) > 12:
                raise ValidationError("10 digits be allowed in %s" % val)

            
    @api.constrains('credit_limit','finace_chgs_ytd','higest_acc_balance','credit_available',
        'running_balance','statment_balance','statment_discount','returns','period_to_date_sale','year_to_date_sale','year_to_date_cost',
            'year_to_date_gp','last_year_sale','last_year_cost','period_to_date_gp_dollor'
            ,'year_to_date__dollor','last_year_gp_dollor','terms_disc','year_to_date_fin_chrgs',
            'last_year_gp_fin_chrgs','year_to_date_returns','year_to_date_transaction',
            'customer_sales_summary','period_to_date_gp','last_year_gp','amount_last_pay','monthly_payment')
    def validate_con_qut_on_hant(self):
        if self.credit_limit:
            val = "Credit Limit"
            self.validate_float(self.credit_limit,val)
        if self.finace_chgs_ytd:
            val = "Finance YTD"
            self.validate_float(self.finace_chgs_ytd,val)
        if self.higest_acc_balance:
            val = "Higest Acc Balance"
            self.validate_float(self.higest_acc_balance,val)        
        if self.credit_available:
            val = "Credit Available"
            self.validate_float(self.credit_available,val)
        if self.running_balance:
            val = "Running Balance"
            self.validate_float(self.running_balance,val)
        if self.statment_balance:
            val = "Statment Balance"
            self.validate_float(self.statment_balance,val)
        if self.statment_discount:
            val = "Statment Discount"
            self.validate_float(self.statment_discount,val)
        if self.returns:
            val = "Returns ($) YTD"
            self.validate_float(self.returns,val)
        if self.period_to_date_sale:
            val = "Period Cost"
            self.validate_float(self.period_to_date_sale,val)
        if self.year_to_date_sale:
            val = "Year Sale"
            self.validate_float(self.year_to_date_sale,val)
        if self.year_to_date_cost:
            val = "Year Cost"
            self.validate_float(self.year_to_date_cost,val)
        if self.year_to_date_gp:
            val = "Year GP %"
            self.validate_float(self.year_to_date_gp,val)
        if self.last_year_sale:
            val = "Last Year Sale"
            self.validate_float(self.last_year_sale,val)
        if self.last_year_cost:
            val = "Last Year Cost"
            self.validate_float(self.last_year_cost,val)
        if self.period_to_date_gp_dollor:
            val = "Period GP $"
            self.validate_float(self.period_to_date_gp_dollor,val)
        if self.year_to_date__dollor:
            val = "Year GP $"
            self.validate_float(self.year_to_date__dollor,val)
        if self.last_year_gp_dollor:
            val = "Last Year GP $"
            self.validate_float(self.last_year_gp_dollor,val)
        if self.terms_disc:
            val = "Terms Disc"
            self.validate_float(self.terms_disc,val)
        if self.year_to_date_fin_chrgs:
            val = "Year Finance Charges"
            self.validate_float(self.year_to_date_fin_chrgs,val)
        if self.last_year_gp_fin_chrgs:
            val = "Last Year Finance Charges"
            self.validate_float(self.last_year_gp_fin_chrgs,val)
        if self.year_to_date_returns:
            val = "year Returns"
            self.validate_float(self.year_to_date_returns,val)
        if self.year_to_date_transaction:
            val = "Year Transations"
            self.validate_float(self.year_to_date_transaction,val)
        if self.customer_sales_summary:
            val = "Customer Sales Summary"
            self.validate_float(self.customer_sales_summary,val)
        if self.period_to_date_gp:
            val = "Period GP %"
            self.validate_float(self.period_to_date_gp,val)
        if self.last_year_gp:
            val = "Last Year GP"
            self.validate_float(self.last_year_gp,val)
        if self.amount_last_pay:
            val = "Amount Last Pay"
            self.validate_float(self.amount_last_pay,val)
        if self.monthly_payment:
            val = "Monthly Payment"
            self.validate_float(self.monthly_payment,val)
   

    # @api.onchange('finace_chgs_ytd')
    # def validate_float_limit(self):
    #     if self.qut_on_hant:
    #         qut_on_hant = self.qut_on_hant
    #         self.validate_qut_on_hant(qut_on_hant)

    @api.depends('statment_balance')
    def _total_stmt_bal(self):
        '''
            Statment Balance =  sum of  journals debit sum - sum of journals credit sum
        '''
        
        invoices_recivable = self.env['account.move.line'].search([('account_id', '=', '121000 Account Receivable'),('partner_id', '=', self.partner_id.id)])
        invoices_payable   = self.env['account.move.line'].search([('account_id', '=', '211000 Account Payable'),('partner_id', '=', self.partner_id.id)])
        invoices            = invoices_recivable + invoices_payable
        credit_total = 0.0
        debit_total = 0.0
        for record in invoices:
            credit_total = credit_total + record.credit
            debit_total  = debit_total + record.debit
        self.statment_balance =  float(debit_total) - float(credit_total)

    @api.depends('running_balance')
    def _total_running_bal(self):
        '''
            Running Balance =  sum of posted journals debit sum - sum of posted journals credit sum
        '''

        invoices_recivable = self.env['account.move.line'].search([('account_id', '=', '121000 Account Receivable'),('partner_id', '=', self.partner_id.id),('parent_state', '=', 'posted')])
        invoices_payable   = self.env['account.move.line'].search([('account_id', '=', '211000 Account Payable'),('partner_id', '=', self.partner_id.id),('parent_state', '=', 'posted')])
        invoices = invoices_recivable + invoices_payable
        credit_total = 0.0
        debit_total = 0.0
        for record in invoices:
            credit_total = credit_total + record.credit
            debit_total  = debit_total + record.debit
        self.running_balance =  float(debit_total) - float(credit_total)

    @api.depends('returns')
    def _total_refund(self):
        '''
            Returns YTD = sum of invoices due amount
        '''
        invoices = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.partner_id.id)])
        total = 0
        for record in invoices:
            total = total + record.amount_residual
        self.returns = float(total)


    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        '''
            validate birth_date 
        '''
        if self.birth_date:
            current_date=datetime.now()
            current_year=current_date.year
            difference = current_year - self.birth_date.year
            if  self.birth_date.year >= current_year or difference < 10:
                raise ValidationError('Invalid DOB.Please enter a valid BIRTH DATE')

    @api.onchange('social_security')
    def _onchange_social_security(self):
        '''
            validate social_security
        '''
        if self.social_security:
            social_security1   =str(self.social_security)
            letters = re.findall("[^0-9]",social_security1)
            for val in letters:
                social_security1 = social_security1.replace(val,'')
            seperator="-"
            start_group =social_security1[:3]
            second_group=social_security1[3:5]
            third_group =social_security1[5:9]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.social_security  = start_group

    @api.onchange('phone')
    def _onchange_phone(self):
        '''
            validate phone number
        '''
        if self.phone:
            phone1   =str(self.phone)
            letters = re.findall("[^0-9]",phone1)
            for val in letters:
                phone1 = phone1.replace(val,'')
            seperator="-"
            start_group =phone1[:3]
            second_group=phone1[3:6]
            third_group =phone1[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.phone  = start_group

        
    @api.onchange('fax')
    def _onchange_fax(self):
        '''
            validate fax
        '''
        if self.fax:
            phone = str(self.fax)
            letters = re.findall("[^0-9]", phone)
            for val in letters:
                phone = phone.replace(val, '')
            seperator = "-"
            start_group = phone[:3]
            second_group = phone[3:6]
            third_group = phone[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.fax= start_group

    @api.onchange('alternate_phone')
    def _onchange_alternate_phone(self):
        '''
            validate alternate phone number
        '''
        if self.alternate_phone:
            phone1   =str(self.alternate_phone)
            letters = re.findall("[^0-9]",phone1)
            for val in letters:
                phone1 = phone1.replace(val,'')
            seperator="-"
            start_group =phone1[:3]
            second_group=phone1[3:6]
            third_group =phone1[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.alternate_phone  = start_group

        
    @api.onchange('alternate_fax')
    def _onchange_alternate_fax(self):
        '''
            validate alternate fax
        '''
        if self.alternate_fax:
            phone = str(self.alternate_fax)
            letters = re.findall("[^0-9]", phone)
            for val in letters:
                phone = phone.replace(val, '')
            seperator = "-"
            start_group = phone[:3]
            second_group = phone[3:6]
            third_group = phone[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.alternate_fax= start_group

    @api.depends('transations')
    def _total_invoices(self):
        '''
            total invoices count
        '''
        current_date=datetime.now()
        current_year=current_date.year
        date = datetime(current_year-1, 12, 31)
        invoices = self.env['account.move'].search([('invoice_date', '>', date),('move_type', '=', 'out_invoice'),('partner_id', '=', self.partner_id.id)])
        self.transations = len(invoices)

    @api.depends('credit_limit')
    def _total_credit(self):
        '''
            Credit available = credit limit - sum of invoices due amount
        '''
        invoices = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.partner_id.id)])
        total = 0
        for record in invoices:
            total = total + record.amount_residual
        for record in self:
            credit_limits = record.credit_limit
        self.credit_available = float(credit_limits) - float(total)


class Credit(models.Model):
    '''
        The class is used to create a one2many relation with the customer class.
    '''
    _name = 'credit'

    customer_ids            = fields.Many2one('my.customer')
    # dept_id                 = fields.Many2one('res.department')
    dept                    = fields.Char('Dept',help='Exportable')
    st                      = fields.Char('St',help='Exportable')
    ptd_sales               = fields.Float('PTD Sales',help='Exportable')
    ptd_cost                = fields.Float('PTD Cost',help='Exportable')
    ptd_gp                  = fields.Float('PTD GP%',help='Exportable')
    ytd_sales               = fields.Float('YTD Sales',help='Exportable')
    ytd_cost                = fields.Float('YTD Cost',help='Exportable')
    ytd_gp                  = fields.Float('YTD GP%',help='Exportable')
    lyr_sales               = fields.Float('LYR Sales',help='Exportable')
    lyr_cost                = fields.Float('LYR Cost',help='Exportable')
    lyr_gp                  = fields.Float('LYR GP%',help='Exportable')

class resCountryState(models.Model):
    _inherit = 'res.country.state'
    '''
        To setup name get function to get code instead of state name
    '''

    def name_get(self):
        result = []
        for row in self:
            name = row.code
            result.append((row.id, name))
        return result

class resCountry(models.Model):
    _inherit = 'res.country'
    '''
        To setup name get function to get code instead of country name
    '''

    def name_get(self):
        result = []
        for row in self:
            name = row.code
            result.append((row.id, name))
        return result
   
class Names(models.Model):
    '''
        The class is used to create a one2many relation with the customer class.
    '''
    _name = 'names'

    customer_ids            = fields.Many2one('my.customer')
    name                    = fields.Char('Name',help='Exportable')
    show_in_POS             = fields.Selection([('y','Y'),('n','N')], "Show In POS", default='y',help='Exportable')
    phone                   = fields.Char('Phone',help='Exportable')
    cell                    = fields.Char('Cell',help='Exportable')
    fax                     = fields.Char('Fax',help='Exportable')
    pager                   = fields.Char('Pager',help='Exportable')
    email                   = fields.Char('Email',help='Exportable')

    @api.onchange('email')
    def validate_mail(self):
        '''
            validate email
        '''
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.onchange('phone')
    def _onchange_phone(self):
        '''
            validate phone number
        '''
        if self.phone:
            phone1   =str(self.phone)
            letters = re.findall("[^0-9]",phone1)
            for val in letters:
                phone1 = phone1.replace(val,'')
            seperator="-"
            start_group =phone1[:3]
            second_group=phone1[3:6]
            third_group =phone1[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.phone  = start_group

    @api.onchange('cell')
    def _onchange_cell(self):
        '''
            validate cell number
        '''
        if self.cell:
            phone1   =str(self.cell)
            letters = re.findall("[^0-9]",phone1)
            for val in letters:
                phone1 = phone1.replace(val,'')
            seperator="-"
            start_group =phone1[:3]
            second_group=phone1[3:6]
            third_group =phone1[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.cell  = start_group

    @api.onchange('fax')
    def _onchange_fax(self):
        '''
            validate fax
        '''
        if self.fax:
            phone = str(self.fax)
            letters = re.findall("[^0-9]", phone)
            for val in letters:
                phone = phone.replace(val, '')
            seperator = "-"
            start_group = phone[:3]
            second_group = phone[3:6]
            third_group = phone[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.fax= start_group

class BalanceMethod(models.Model):
    '''
        The class is used to create a Many2one relation with the balance_method field in customer class.
    '''
    _name = 'balance'

    name                    = fields.Char('Balance Method',help='Exportable')

class Terms(models.Model):
    '''
        The class is used to create a Many2one relation with the terms_code field in customer class.
    '''
    _name = 'terms'

    name                    = fields.Char('Terms code',help='Exportable')

class Job(models.Model):
    '''
        The class is used to create a Many2one relation with the job field in customer class.
    '''
    _name = 'job'

    name                    = fields.Char('Job',help='Exportable')

class Sort(models.Model):
    '''
        The class is used to create a Many2one relation with the sort_name field in customer class.
    '''
    _name = 'sort'

    name                    = fields.Char('Sort Name',help='Exportable')

    @api.onchange('name')
    def _onchange_sort_name_id(self):
        '''
            validate sort_name_id number
        '''
        if self.name:
            name1   =str(self.name)
            letters = re.findall("[a-zA-Z]",name1)
            for val in letters:
                name1 = name1.replace(val,'')
        
            self.name  = name1
        

class Bill(models.Model):
    '''
        The class is used to create a Many2one relation with the bill_to field in customer class.
    '''
    _name = 'bill'

    name                    = fields.Char('Bill To',help='Exportable')

class Category(models.Model):
    '''
        The class is used to create a Many2one relation with the Category field in customer class.
    '''
    _name = 'category'

    name                    = fields.Char('Category Plan',help='Exportable')

class AccountPaymentInherit(models.Model):
    '''
        Inherits account.payment model
    '''
    _inherit = 'account.payment'

    now_due = fields.Float('Now Due')
    stmt_disc = fields.Char('Stmt Disc')
    net_due = fields.Float('Net Due')
    running_bal = fields.Float('Running Bal')
    last_pay_date = fields.Date('Last Pay Date')
    apply_to = fields.Char('Apply To')
    due_date = fields.Date('Due Date')
    allowance = fields.Float('Allowance')
    total = fields.Float('Total')
    codes = fields.Char('Codes')
    ar_note = fields.Char('A/R Note')
    st = fields.Char('St')
    discount = fields.Char('Discount Taken')