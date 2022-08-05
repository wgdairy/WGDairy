# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re


class vendors(models.Model):
    '''
        Inherits partner module
    '''
    _name = "wgd.vendors"
    _inherits = {"res.partner": 'partner_id'}
    _columns = {
        'partner_id' : fields.Many2one('wgd.vendors', 'Vendor Details', help="Link this vendor to it's partner", ondelete='cascade', required=True)
    }

    # main tab fields
    vendor = fields.Char('Vendor')
    vendor_name = fields.Char('Name')
    sort_name = fields.Selection([],'Sort Name')
    pay_to_vendor = fields.Selection([],'Pay To Vendor')
    pay_to_vendor2 = fields.Selection([], 'Pay to Vendor')
    phone = fields.Char('Phone')
    phone2 = fields.Char('Alternate Phone')
    fax = fields.Char('Fax')
    contact = fields.Char('Contact')
    assignee = fields.Char('Assigned Customer')
    vType = fields.Selection([],'Type')
    codes = fields.Integer('Codes')
    network_id = fields.Char('Network ID')
    network_id_code = fields.Char('Network ID Code')
    po_item_number = fields.Selection([],'PO Item Number')
    edi_po = fields.Selection([],'EDI PO')
    edi_translation = fields.Selection([],'EDI Translation')
    alternate_fax = fields.Char('Alternate Fax')
    img_id = fields.Selection([],'Catalog Image ID')
    last_payment = fields.Date('Last Payment')

    # order info fields 
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    minimum_dollars = fields.Monetary('Minimum Dollars')
    minimum_dollars_code = fields.Integer('Minimum Dollars Code')
    minimum_weight = fields.Float('Minimum Weight')
    minimum_weight_code = fields.Integer('Minimum Weight Code')
    minimum_units = fields.Float('Minimum Units')
    minimum_units_code = fields.Integer('Minimum Units Code')
    minimum_bill = fields.Integer('Minimum Bill')
    minimum_bill_code = fields.Integer('Minimum Bill Code')
    minimum_po = fields.Integer('Minimum PO Line')
    annual_dollars = fields.Monetary('Annual Dollars')
    annual_units = fields.Float('Annual Units')
    lead_time = fields.Char('Lead Time')
    update_lead_time = fields.Selection([],'Update Lead Time')
    backorder = fields.Selection([], "Backorder")
    print_date_due = fields.Selection([], "Print Date Due")
    freight_policy = fields.Selection([],'Fraight Policy')
    drop_ship = fields.Selection([], 'Drop/Ship')
    ship = fields.Char('Ship Via')
    addertype = fields.Selection([],'Adder Type')
    dropship_certified = fields.Selection([],'Dropship Certified')
    buyer_id = fields.Selection([], "Buyer's ID")


    # accounts payable tab
    acc_num = fields.Char('Account Number')
    auto_distribute = fields.Selection([], 'Auto Distribute')
    federal_id_type = fields.Selection([], 'Federal ID Type')
    federal_id = fields.Char('Federal ID')
    temp_perm = fields.Selection([], "Temp/Perm")
    category = fields.Selection([], '1099 Category')
    last_activity = fields.Date('Last Activity Date')
    vendor_status = fields.Selection([], 'Vendor Status')
    append_rv = fields.Selection([], 'Append To RV')
    bank_code = fields.Selection([], 'Bank Code')
    terms_code = fields.Selection([], 'Terms Code')
    terms_type = fields.Selection([], 'Terms Type')
    due_days = fields.Integer('Due Days')
    disc_days = fields.Integer('Disc Days')
    discount = fields.Integer('Discount %')
    print_check = fields.Selection([], 'Print on Checks')
    vendor_language = fields.Selection([], 'Vendor Language')
    remit_address = fields.Char('Address')
    remit_street1 = fields.Char('Address')
    remit_street2 = fields.Char('Address')
    remit_city = fields.Char('City')
    remit_state = fields.Char('State')
    remit_country = fields.Char('Country')
    zip_code = fields.Char('Zip Code')

    # history tab 
    amount_paid1 = fields.Integer('Amount Paid')
    amount_paid2 = fields.Integer('Amount Paid')
    discount_taken1 = fields.Integer('Discounts Taken')
    discount_taken2 = fields.Integer('Discounts Taken')
    discount_lost1 = fields.Integer('Discount_lost')
    discount_lost2 = fields.Integer('Discount_lost')
    vendor_bal_due = fields.Float('Vendor Balance Due')
    ''' 
        cq for 'Current Qtr' lq for 'Last Qtr'
        b for 'Buys' field , ytd for YearToDate, ly for LastYear
    '''
    warehouse_cq = fields.Integer('Warehouse ($/Buys)')
    warehouse_cq_b = fields.Integer()
    warehouse_lq = fields.Integer()
    warehouse_lq_b = fields.Integer()
    warehouse_ytd = fields.Integer()
    warehouse_ytd_b = fields.Integer()
    warehouse_ly = fields.Integer()
    warehouse_ly_b = fields.Integer()

    drop_ship  = fields.Integer('Drop/Ship')
    special = fields.Char('Special')
    
    units_ordered = fields.Integer('Units Ordered')
    received = fields.Date('Recieved')
    last_received = fields.Date('Last Recieved')

    #Notes Tab
    note_group = fields.Integer('Note Group')
    note_type = fields.Integer('Type')
    display_repeats = fields.Selection([], 'Display Repeats')
    print_repeats = fields.Selection([], 'Print Repeats')
    message = fields.Text('Message')

    # phone number validation 
    @api.onchange('phone')
    def _onchange_phone(self):
        '''
            validate phone number
        '''
        if self.phone:
            phone   =str(self.phone)
            letters = re.findall("[^0-9]",phone)
            for val in letters:
                phone = phone.replace(val,'')
            seperator="-"
            start_group =phone[:3]
            second_group=phone[3:6]
            third_group =phone[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.phone  = start_group

    @api.onchange('phone2')
    def _onchange_phone2(self):
        '''
            validate alternate phone number
        '''
        if self.phone:
            phone   =str(self.phone2)
            letters = re.findall("[^0-9]",phone)
            for val in letters:
                phone = phone.replace(val,'')
            seperator="-"
            start_group =phone[:3]
            second_group=phone[3:6]
            third_group =phone[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.phone2  = start_group

    @api.onchange('contact')
    def _onchange_contact(self):
        '''
            validate contact number
        '''
        if self.phone:
            contact   =str(self.contact)
            letters = re.findall("[^0-9]",contact)
            for val in letters:
                contact = contact.replace(val,'')
            seperator="-"
            start_group =contact[:3]
            second_group=contact[3:6]
            third_group =contact[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.contact  = start_group
        
    @api.onchange('fax')
    def _onchange_fax(self):
        '''
            validate fax number
        '''
        if self.fax:
            fax   =str(self.fax)
            letters = re.findall("[^0-9]",fax)
            for val in letters:
                fax = fax.replace(val,'')
            seperator="-"
            start_group =fax[:3]
            second_group=fax[3:6]
            third_group =fax[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.fax  = start_group

    @api.onchange('alternate_fax')
    def _onchange_fax2(self):
        '''
            validate alternate fax number
        '''
        if self.alternate_fax:
            alternate_fax   =str(self.alternate_fax)
            letters = re.findall("[^0-9]",alternate_fax)
            for val in letters:
                alternate_fax = alternate_fax.replace(val,'')
            seperator="-"
            start_group =alternate_fax[:3]
            second_group=alternate_fax[3:6]
            third_group =alternate_fax[6:10]
            start_group += seperator
            start_group += second_group
            start_group += seperator
            start_group += third_group
            self.alternate_fax  = start_group

    


class AccountMove(models.Model):
    '''
    Inherits account.move model
    '''
    _inherit = 'account.move'

    doc = fields.Char('Doc#')
    doc_date = fields.Date('Doc')
    discount_allowed = fields.Float('Discount Allowed')
    discount_take = fields.Float('Discount To Take', related='line_ids.discount')
    allowance = fields.Float('Allowance')
    amount_paid = fields.Float('Amount Paid')
    net_balance = fields.Float('Net Balance')
    days_past_disc = fields.Integer('Days Past Discount')
    action = fields.Char('Action')
    ar_note = fields.Char('A/R Note')
    balance = fields.Float('Balance')
    stmnt_disc = fields.Char('Stmnt Disc')
    running_bal = fields.Float('Running Bal')
    stmt_disc = fields.Char('Stmt Disc')
    last_pay_date = fields.Date('Last Pay Date')
    invoice_date = fields.Date(string='Doc Date')





    