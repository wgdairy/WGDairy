from odoo import fields, models, api #, re
import re

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


    
    customer_id             = fields.Char("Customer ID",help='Exportable')
    partner_id              = fields.Many2one('res.partner')    
    job_id                  = fields.Many2one('job')
    sort_name_id            = fields.Many2one('sort')
    bill_to_id              = fields.Many2one('bill')
    ace_rewards             = fields.Char("Ace Rewards",help='Exportable')

    # notebook page1 Main
    phone                   = fields.Char('Phone',help='Exportable')
    fax                     = fields.Char('Fax',help='Exportable')
    contact                 = fields.Char('contact',help='Exportable')

    credit_message1         = fields.Char(' ',help='Exportable')
    credit_message2         = fields.Char(' ',help='Exportable')

    credit_limit            = fields.Float("Credit Limit")
    trade_discount          = fields.Char('Trade Discount %',help='Exportable')
    account_code1           = fields.Char('account_code1',help='Exportable')
    monthly_payment         = fields.Integer('Monthly Payment',help='Exportable')
    # category_plan           = fields.Many2one("", string='Category Plan', ondelete='restrict',help='Exportable')
    # tax_code                = fields.Many2one("", string='Tax Code', ondelete='restrict',help='Exportable')
    # salesperson             = fields.Many2one("", string='Salesperson', ondelete='restrict',help='Exportable')
    # terms_code              = fields.Many2one("", string='Terms Code', ondelete='restrict',help='Exportable')
    category_plan_id        = fields.Many2one('category')
    tax_code                = fields.Selection([('yes','Y'),('no','N')], "Tax Code", default='yes',help='Exportable')
    salesperson             = fields.Selection([('yes','Y'),('no','N')], "Salesperson", default='no',help='Exportable')
    terms_code              = fields.Selection([('yes','Y'),('no','N')], "Terms Code", default='no')
    pure_archive_invoices   = fields.Char('Pure Archive Invoices',help='Exportable')

    po_required             = fields.Selection([('yes','Y'),('no','N')], "PO Required", default='no',help='Exportable')
    default_po              = fields.Char('Default PO',help='Exportable')
    
    balance_method          = fields.Selection([('yes','0'),('no','0')], "Balance Method", default='no')
    charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed", default='yes',help='Exportable')
    std_sell_price          = fields.Selection([('yes','R'),('no','R')], "Std Sell Price/POS", default='no',help='Exportable')
    finace_charges          = fields.Selection([('yes','Y'),('no','N')], "Finace Charges", default='no')
    store_acct_opened_id    = fields.Many2one('res.company')
    transfer_to_store       = fields.Selection([('yes','Y'),('no','N')], "Transfer To Store", default='no',help='Exportable')
    print_statments         = fields.Selection([('yes','Y'),('no','N')], "Print Statments", default='no')
    # charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed", default='yes',help='Exportable')
    check_allowed           = fields.Selection([('yes','Y'),('no','N')], "Check Allowed", default='no',help='Exportable')
    credit_are_only         = fields.Selection([('yes','Y'),('no','N')], "Credit A/R Only", default='no',help='Exportable')
    taxable                 = fields.Selection([('yes','Y'),('no','N')], "Taxable", default='no')
    keep_dept_history       = fields.Selection([('yes','Y'),('no','N')], "Keep Dept History", default='yes',help='Exportable')
    print_invoices_in_pos   = fields.Selection([('yes','Y'),('no','N')], "Print Invoices In POS", default='no',help='Exportable')
    

# notebook page2 Credit
    finace_chgs_ytd         = fields.Float("Finace Chgs YTD")
    #credit_limit_2          = fields.Integer("Credit Limit")
    higest_acc_balance      = fields.Float("Higest Acct Balance")
    credit_available        = fields.Float("Credit Available")
    running_balance         = fields.Float("Running Balance")
    statment_balance        = fields.Float("Statment Balance")
    statment_discount       = fields.Float("Statment Discount")
    returns                 = fields.Float("Returns")
    transations             = fields.Float("Transations")

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
    amount_last_pay         = fields.Float("Amount Last Pay")
    special_charges         = fields.Integer("Special Charges")


# notebook page3 Dept
    store                   = fields.Selection([('1','1'),('2','2')], "Store", default='1',help='Exportable')
    std_sell_prices         = fields.Integer("Std Sell Price")
    delete_all              = fields.Boolean(string = "Delete All Department History?", required = True)
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

    of_times_no_activity    = fields.Integer("No Activity")
    of_times_current        = fields.Integer("Current")
    of_times_1_30           = fields.Integer("1 - 30")
    of_times_31_60          = fields.Integer("31 - 60")
    of_times_61_90          = fields.Integer("61 - 90")
    of_times_over_90        = fields.Integer("Over 90")

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

# notebook page6 Misc
    social_security         = fields.Char('Social Security',help='Exportable')
    birth_date              = fields.Date("Birth Date")
    pst_registration        = fields.Char('PST Regisration',help='Exportable')
    gst_registration        = fields.Char('GST Regisration',help='Exportable')
    pesticide_license       = fields.Char('Pesticide License',help='Exportable')
    pesticide_lic_exp       = fields.Char('Pesticide Lic. Exp.',help='Exportable')
    freght_factor           = fields.Char('Freght Factor',help='Exportable')
    rescale_code            = fields.Char('Rescale Code',help='Exportable')
    alternate_phone         = fields.Char('Alternative Phone',help='Exportable')
    alternate_fax           = fields.Char('Alternative Fax',help='Exportable')
    open_quote_1            = fields.Char('Open Quote Doc#/St',help='Exportable')
    open_quote_2            = fields.Char('',help='Exportable')
    rebate_plan             = fields.Selection([('1',' '),('2','2')], "Rebate Plan",help='Exportable')
    
    business_type           = fields.Selection([('1',' '),('2','2')], "Business Type",help='Exportable')
    location                = fields.Selection([('1',' '),('2','2')], "Location",help='Exportable')
    customer_rank           = fields.Selection([('1',' '),('2','2')], "Customer Rank",help='Exportable')
    statment_type           = fields.Selection([('1',' '),('2','2')], "Statment Type",help='Exportable')

    statment_fmt            = fields.Selection([('1',' '),('2','2')], "Statment/Fmt",help='Exportable')
    statment_fmt2           = fields.Selection([('1',' '),('2','2')], "",help='Exportable')
    Invoice_credit          = fields.Selection([('1',' '),('2','2')], "Invoice/Credit",help='Exportable')
    order_sp_ord_estimate   = fields.Selection([('1',' '),('2','2')], "Order/Sp.Ord/Estimate",help='Exportable')

    fax_pos_stmt            = fields.Selection([('1',' '),('2','2')], "Fax POS/Stmt",help='Exportable')
    fax_pos_stmt1           = fields.Selection([('1',' '),('2','2')], "Fax POS/Stmt",help='Exportable')
    ace_rewards_status      = fields.Selection([('1','A'),('2','2')], "Ace Rewards Status",default='1',help='Exportable')
    tax_override_plan       = fields.Selection([('1',' '),('2','2')], "Tax Override Plan",help='Exportable')
    
    prompt_in_pos           = fields.Selection([('1',' '),('2','2')], "Prompt in POS?",help='Exportable')
    prompt_threshold        = fields.Char('Prompt Threshold',help='Exportable')
   
    price_pick_ticket       = fields.Selection([('y','Y'),('n','N')], "Price Pick Ticket", default='y',help='Exportable')
    open_quotes             = fields.Selection([('y','Y'),('n','N')], "Open Quote", default='n',help='Exportable')
    global_credit_check     = fields.Selection([('1',' '),('2','2')], "Global Credit Check",help='Exportable')
    print_lumber_totals     = fields.Selection([('y','Y'),('n','N')], "Print Lumber Totals", default='y',help='Exportable')
    # store_job_opened        = fields.Selection([('1','1'),('2','2')], "Store Job Opened", default='1',help='Exportable')
    default_price_um        = fields.Selection([('1',' '),('2','2')], "Default Price UM",help='Exportable')
    statment_by_job         = fields.Selection([('s','S')], "Statment By Job", default='s',help='Exportable')

    additional_flag          = fields.Char('Additional Flags',help='Exportable')
    
# notebook page7 Names
    names_ids              = fields.One2many('names', 'customer_ids',string=" ") 

# notebook page8 Note
    types                   = fields.Selection([('1','1'),('2','2')], "Type", default='1',help='Exportable')
    display_repeat          = fields.Selection([('yes','Y'),('no','N')], "Display Repeats", default='yes',help='Exportable')
    print_repeat            = fields.Selection([('yes','Y'),('no','N')], "Print Repeats", default='no',help='Exportable')                 
    message                 = fields.Html("Message")

    def button_(self):
        '''
            For button action
        '''
        x = 10

    def action_student_schedules(self):
        pass
    
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