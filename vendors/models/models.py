# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class vendors(models.Model):
    '''
        Inherits partner module
    '''
    _name = "wgd.vendors"
    _inherits = {"res.partner": 'partner_id'}

    # main tab fields
    partner_id = fields.Many2one('res.partner', 'Vendor Details', help="Link this vendor to it's partner", ondelete='cascade', required=True)
    vendor = fields.Char('Vendor')
    sort_name = fields.Char('Sort Name')
    pay_to_vendor = fields.Many2one('res.partner','Pay To Vendor')
    pay_to_vendor2 = fields.Many2one('res.partner', 'Pay to Vendor')
    phone = fields.Char('Phone')
    phone2 = fields.Char('Alternate Phone')
    # function for getting 'United States' as default country 
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'US')], limit=1)
        return country
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)

    fax = fields.Char('Fax')
    contact = fields.Char('Contact')
    assignee = fields.Many2one('res.partner','Assigned Customer')
    vType = fields.Selection([('w','W'),('i','I')],'Type')
    codes = fields.Integer('Codes')
    network_id = fields.Char('Network ID')
    network_id_code = fields.Char('Network ID Code')
    po_item_number = fields.Selection([],'PO Item Number')
    edi_po = fields.Selection([],'EDI PO')
    edi_translation = fields.Selection([],'EDI Translation')
    alternate_fax = fields.Char('Alternate Fax')
    img_id = fields.Selection([],'Catalog Image ID')
    # function to get year as a list
    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list
    lp_year = fields.Selection(year_selection, string="Year") #lp : last payment
    lp_month = fields.Selection([('1','1'),('2','2'),('3','3'),
                                 ('4','4'),('5','5'),('6','6'),
                                 ('7','7'),('8','8'),('9','9'),
                                 ('10','10'),('11','11'),('12','12'),],string='Month')

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
    update_lead_time = fields.Selection([('yes','Y'),('no','N')],'Update Lead Time')
    backorder = fields.Selection([('yes','Y'),('no','N')], "Backorder")
    print_date_due = fields.Selection([('yes','Y'),('no','N')], "Print Date Due")
    freight_policy = fields.Selection([('yes','Y'),('no','N')],'Fraight Policy')
    drop_ship = fields.Selection([('yes','Y'),('no','N')], 'Drop/Ship')
    ship_via = fields.Char('Ship Via')
    addertype = fields.Selection([],'Adder Type')
    dropship_certified = fields.Selection([],'Dropship Certified')
    buyer_id = fields.Selection([], "Buyer's ID")


    # accounts payable tab
    acc_num = fields.Selection([],'Account Number')
    acc_num2 = fields.Selection([],'Account Number')
    auto_distribute = fields.Selection([], 'Auto Distribute')
    federal_id_type = fields.Selection([('Federal ID', 'F'), ('Social Security', 'S')], 'Federal ID Type')
    federal_id = fields.Char('Federal ID')
    temp_perm = fields.Selection([], "Temp/Perm")
    category = fields.Selection([], '1099 Category')
    last_activity = fields.Date('Last Activity Date')
    vendor_status = fields.Selection([], 'Vendor Status')
    append_rv = fields.Selection([], 'Append To RV')
    bank_code = fields.Selection([], 'Bank Code')
    terms_code = fields.Many2one('account.payment.term', 'Terms Code')
    terms_type = fields.Selection([], 'Terms Type',related='terms_code.terms_type')
    due_days = fields.Integer('Due Days',related='terms_code.line_ids.days')
    disc_days = fields.Integer('Disc Days',related='terms_code.disc_days')
    discount = fields.Integer('Discount %', related='terms_code.discount')
    print_check = fields.Selection([], 'Print on Checks')
    vendor_language = fields.Selection([], 'Vendor Language')
    remit_address = fields.Char('Address')
    remit_street1 = fields.Char('Address')
    remit_street2 = fields.Char('Address')
    remit_city = fields.Char('City')
    remit_state = fields.Many2one('res.country.state', string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    remit_country = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)
    zip_code = fields.Char('Zip Code')

    # history tab 
    amount_paid1 = fields.Float('Amount Paid')
    amount_paid2 = fields.Float('Amount Paid')
    discount_taken1 = fields.Float('Discounts Taken')
    discount_taken2 = fields.Float('Discounts Taken')
    discount_lost1 = fields.Float('Discount_lost')
    discount_lost2 = fields.Float('Discount_lost')
    vendor_bal_due = fields.Float('Vendor Balance Due')
    ''' 
        cq for 'Current Qtr' lq for 'Last Qtr'
        b for 'Buys' field , ytd for YearToDate, ly for LastYear
    '''
    warehouse_cq = fields.Float('Warehouse ($/Buys)')
    warehouse_cq_b = fields.Integer()
    warehouse_lq = fields.Float()
    warehouse_lq_b = fields.Integer()
    warehouse_ytd = fields.Float()
    warehouse_ytd_b = fields.Integer()
    warehouse_ly = fields.Float()
    warehouse_ly_b = fields.Integer()

    dropshiip_cq = fields.Monetary('Drop/Ship')
    dropshiip_lq = fields.Monetary()
    dropshiip_ytd = fields.Monetary()
    dropshiip_ly = fields.Monetary()

    special_cq = fields.Monetary('Special')
    special_lq = fields.Monetary()
    special_ytd = fields.Monetary()
    special_ly = fields.Monetary()
    
    units_ordered_ytd = fields.Integer('Units Ordered')
    units_ordered_ly = fields.Integer('Units Ordered')
    received_ytd = fields.Float('Recieved')
    recieved_ytd_fill = fields.Integer('Recieved YTD Fill', readonly=True)
    received_ly = fields.Float('Recieved')
    recieved_ly_fill = fields.Integer('Recieved LY Fill', readonly=True)
    last_received = fields.Date('Last Recieved')

    #Notes Tab
    note_group = fields.Integer('Note Group')
    note_type = fields.Selection([],'Type')
    display_repeats = fields.Selection([], 'Display Repeats')
    print_repeats = fields.Selection([], 'Print Repeats')
    message = fields.Text('Message')

    # Contact Tab
    contact_ids = fields.One2many('contact.lines', 'vendor', string="")

    filter_by_vname = fields.Many2one('wgd.vendors')
    filter_by_vid = fields.Many2one('wgd.vendors')

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('hide_code'):
                name = rec.name
            else:
                name = rec.vendor
            result.append((rec.id, name))
        return result
    
    def write(self, vals):
        if 'vendor' in vals:
            vendor_dup = self.env['wgd.vendors'].search([('vendor','=',vals['vendor'])])
            if len(vendor_dup) > 0:
                raise ValidationError('Vendor ID already exists')
        else:
            res = super(vendors, self).write(vals)
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name :
            args += ['|' , ('name', operator, name), ('vendor', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.onchange('filter_by_vname')
    def onchange_by_name(self):
        if self.filter_by_vname:
            self.filter_by_vid = False
            name = self.env['wgd.vendors'].search([('id','=',self.filter_by_vname.id)],limit=1)
            self.vendor = name.vendor
            self.name = name.name
            self.sort_name = name.sort_name
            self.pay_to_vendor = name.pay_to_vendor
            self.pay_to_vendor2 = name.pay_to_vendor2
            self.company_id = name.company_id

            self.phone = name.phone
            self.assignee = name.assignee
            self.phone2 = name.phone2
            self.fax = name.fax
            self.contact = name.contact
            self.vType = name.vType
            self.codes = name.codes
            self.street = name.street
            self.street2 = name.street2
            self.city = name.city
            self.state_id = name.state_id
            self.zip = name.zip
            self.country_id = name.country_id
            self.lead_time = name.lead_time
            self.update_lead_time = name.update_lead_time

    @api.onchange('filter_by_vid')
    def onchange_by_id(self):
        if self.filter_by_vid:
            self.filter_by_vname = False
            name = self.env['wgd.vendors'].search([('id','=',self.filter_by_vid.id)],limit=1)
            self.vendor = name.vendor
            self.name = name.name
            self.sort_name = name.sort_name
            self.pay_to_vendor = name.pay_to_vendor
            self.pay_to_vendor2 = name.pay_to_vendor2
            self.company_id = name.company_id

            self.phone = name.phone
            self.assignee = name.assignee
            self.phone2 = name.phone2
            self.fax = name.fax
            self.contact = name.contact
            self.vType = name.vType
            self.codes = name.codes
            self.street = name.street
            self.street2 = name.street2
            self.city = name.city
            self.state_id = name.state_id
            self.zip = name.zip
            self.country_id = name.country_id
            self.lead_time = name.lead_time
            self.update_lead_time = name.update_lead_time


    # function to validate float fields,
    #    when digits is more than 10
    def validate_float(self, float_value, val):
        if float_value:
            if len(str(float_value)) > 12:
                raise ValidationError("10 digits be allowed in %s" % val)
    
    # validation for monetary fields with more than 10 digits
    @api.constrains('amount_paid1','amount_paid2','discount_taken1','discount_taken2',
                    'discount_lost1','discount_lost2','warehouse_cq','warehouse_lq'
                    'warehouse_ytd','warehouse_ly','received_ytd','received_ly')
    def validate_monetary_fields(self):
        if self.amount_paid1:
            val = "Amount Paid"
            self.validate_float(self.amount_paid1,val)
        if self.amount_paid2:
            val = "Amount Paid"
            self.validate_float(self.amount_paid2,val)
        if self.discount_taken1:
            val = "Discount Taken"
            self.validate_float(self.discount_taken1,val)
        if self.discount_taken2:
            val = "Discount Taken"
            self.validate_float(self.discount_taken2,val)
        if self.discount_lost1:
            val = "Discount Lost"
            self.validate_float(self.discount_lost1,val)
        if self.discount_lost2:
            val = "Discount Lost"
            self.validate_float(self.discount_lost2,val)
        if self.warehouse_cq:
            val = "Warehouse Current Qtr"
            self.validate_float(self.warehouse_cq,val)
        if self.warehouse_lq:
            val = "Warehouse Last Qtr"
            self.validate_float(self.warehouse_lq,val)
        if self.warehouse_ytd:
            val = "Warehouse Year To Date"
            self.validate_float(self.warehouse_ytd,val)
        if self.warehouse_ly:
            val = "Warehouse Last Year"
            self.validate_float(self.warehouse_ly,val)
        if self.received_ytd:
            val = "Recieved Year To Date"
            self.validate_float(self.received_ytd,val)
        if self.received_ly:
            val = "Recieved Last Year"
            self.validate_float(self.received_ly,val)

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
        if self.phone2:
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

    # @api.onchange('contact')
    # def _onchange_contact(self):
    #     '''
    #         validate contact number
    #     '''
    #     if self.contact:
    #         contact   =str(self.contact)
    #         letters = re.findall("[^0-9]",contact)
    #         for val in letters:
    #             contact = contact.replace(val,'')
    #         seperator="-"
    #         start_group =contact[:3]
    #         second_group=contact[3:6]
    #         third_group =contact[6:10]
    #         start_group += seperator
    #         start_group += second_group
    #         start_group += seperator
    #         start_group += third_group
    #         self.contact  = start_group
        
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
    
    def button_(self):
        pass

    
    
class ContactLines(models.Model):
    '''
        Model for Contact tab in vendor form.
    '''
    _name = 'contact.lines'

    vendor = fields.Many2one('wgd.vendors')
    name = fields.Char('Name')
    phone = fields.Char('Phone')
    cell = fields.Integer('Cell')
    fax = fields.Char('Fax')
    pager = fields.Char('Pager')
    email = fields.Char('Email')
    title = fields.Char('Title')
    comments = fields.Char('Comments')
    primary = fields.Char('Primary')
    purchase_orders = fields.Char('Purchase Orders')

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

    # fax number validation 
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


# class MonthlyStatement(models.AbstractModel):
#     _inherit = ['account.partner.ledger']

#     @api.model
#     def _get_report_name(self):
#         return _('Monthly Statement')


class PaymentTerms(models.Model):
    _inherit = 'account.payment.term'

    due_days = fields.Integer('Due Days')
    disc_days = fields.Integer('Disc Days')
    discount = fields.Integer('Discount%')
    terms_type = fields.Selection([],'Terms Type')



class stateModel(models.Model):
    '''
    Inherits res.country.state model
    '''
    _inherit = 'res.country.state'

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}".format(record.code)))
        return result

class companyModel(models.Model):
    '''
    Inherits res.company model.
    '''
    _inherit = 'res.company'

    company_name = fields.Char('Company Name')