# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
import odoo.addons.decimal_precision as dp
from datetime import date, datetime


class vendors(models.Model):
    '''
        Inherits partner module
    '''
    _name = "wgd.vendors"
    _inherits = {"res.partner": 'partner_id'}
    _order = "name asc"

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
                if rec.vendor:
                    name = rec.vendor
                else:
                    name = rec.name
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
    def create(self, vals):
        print(self.vendor, vals['vendor'])
        if 'vendor' in vals or 'company_id' in vals:
            vendor_dup = self.env['wgd.vendors'].search([('vendor','=',vals['vendor']),('company_id', '=', vals['company_id'])])
            if len(vendor_dup) > 0:
                raise ValidationError(f'Vendor ID ({vendor_dup.vendor}) already exists')
        res = super(vendors, self).create(vals)
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

            self.print_date_due = name.print_date_due
            self.backorder = name.backorder
            self.freight_policy = name.freight_policy
            self.drop_ship = name.drop_ship
            self.ship_via = name.ship_via
            self.po_item_number = name.po_item_number
            self.edi_po = name.edi_po
            self.edi_translation = name.edi_translation
            self.alternate_fax = name.alternate_fax
            self.img_id = name.img_id
            self.lp_year = name.lp_year
            self.lp_month = name.lp_month
            self.message = name.message
            self.auto_distribute = name.auto_distribute
            self.federal_id_type = name.federal_id_type
            self.federal_id = name.federal_id
            self.temp_perm = name.temp_perm
            self.category = name.category
            self.last_activity = name.last_activity
            self.append_rv = name.append_rv
            self.terms_code = name.terms_code
            self.due_days = name.due_days
            self.terms_type = name.terms_type
            self.disc_days = name.disc_days
            self.discount = name.discount
            self.print_check = name.print_check
            self.remit_address = name.remit_address
            self.remit_street1 = name.remit_street1
            self.remit_street2 = name.remit_street2
            self.remit_city = name.remit_city
            self.remit_state = name.remit_state
            self.zip_code = name.zip_code
            self.remit_country = name.remit_country
            self.amount_paid1 = name.amount_paid1
            self.amount_paid2 = name.amount_paid2
            self.discount_taken1 = name.discount_taken1
            self.discount_taken2 = name.discount_taken2
            self.discount_lost1 = name.discount_lost1
            self.discount_lost2 = name.discount_lost2
            self.vendor_bal_due = name.vendor_bal_due
            self.warehouse_cq = name.warehouse_cq
            self.warehouse_cq_b = name.warehouse_cq_b
            self.warehouse_lq = name.warehouse_lq
            self.warehouse_lq_b = name.warehouse_lq_b
            self.warehouse_ytd = name.warehouse_ytd
            self.warehouse_ytd_b = name.warehouse_ytd_b
            self.warehouse_ly = name.warehouse_ly
            self.warehouse_ly_b = name.warehouse_ly_b
            self.units_ordered_ytd = name.units_ordered_ytd
            self.units_ordered_ly = name.units_ordered_ly
            self.received_ytd = name.received_ytd
            self.recieved_ytd_fill = name.recieved_ytd_fill
            self.recieved_ly_fill = name.recieved_ly_fill
            self.received_ly = name.received_ly
            self.last_received = name.last_received


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

            self.print_date_due = name.print_date_due
            self.backorder = name.backorder
            self.freight_policy = name.freight_policy
            self.drop_ship = name.drop_ship
            self.ship_via = name.ship_via
            self.po_item_number = name.po_item_number
            self.edi_po = name.edi_po
            self.edi_translation = name.edi_translation
            self.alternate_fax = name.alternate_fax
            self.img_id = name.img_id
            self.lp_year = name.lp_year
            self.lp_month = name.lp_month
            self.message = name.message
            self.auto_distribute = name.auto_distribute
            self.federal_id_type = name.federal_id_type
            self.federal_id = name.federal_id
            self.temp_perm = name.temp_perm
            self.category = name.category
            self.last_activity = name.last_activity
            self.append_rv = name.append_rv
            self.terms_code = name.terms_code
            self.due_days = name.due_days
            self.terms_type = name.terms_type
            self.disc_days = name.disc_days
            self.discount = name.discount
            self.print_check = name.print_check
            self.remit_address = name.remit_address
            self.remit_street1 = name.remit_street1
            self.remit_street2 = name.remit_street2
            self.remit_city = name.remit_city
            self.remit_state = name.remit_state
            self.zip_code = name.zip_code
            self.remit_country = name.remit_country
            self.amount_paid1 = name.amount_paid1
            self.amount_paid2 = name.amount_paid2
            self.discount_taken1 = name.discount_taken1
            self.discount_taken2 = name.discount_taken2
            self.discount_lost1 = name.discount_lost1
            self.discount_lost2 = name.discount_lost2
            self.vendor_bal_due = name.vendor_bal_due
            self.warehouse_cq = name.warehouse_cq
            self.warehouse_cq_b = name.warehouse_cq_b
            self.warehouse_lq = name.warehouse_lq
            self.warehouse_lq_b = name.warehouse_lq_b
            self.warehouse_ytd = name.warehouse_ytd
            self.warehouse_ytd_b = name.warehouse_ytd_b
            self.warehouse_ly = name.warehouse_ly
            self.warehouse_ly_b = name.warehouse_ly_b
            self.units_ordered_ytd = name.units_ordered_ytd
            self.units_ordered_ly = name.units_ordered_ly
            self.received_ytd = name.received_ytd
            self.recieved_ytd_fill = name.recieved_ytd_fill
            self.recieved_ly_fill = name.recieved_ly_fill
            self.received_ly = name.received_ly
            self.last_received = name.last_received


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


class VendorContact(models.Model):
    _inherit = "res.partner"

    #Customer vendor seprator
    is_customer_vendor = fields.Selection(string='Contact Type', selection=[('is_customer', 'Customer'), ('is_vendor', 'Vendor')], default='is_customer')

    # main tab fields
    vendor = fields.Char('Vendor')
    sort_name = fields.Char('Sort Name')
    pay_to_vendor = fields.Many2one('res.partner','Pay To Vendor')
    pay_to_vendor2 = fields.Many2one('res.partner', 'Pay to Vendor')
    # phone = fields.Char('Phone')
    phone2 = fields.Char('Alternate Phone')
    # function for getting 'United States' as default country 
    # @api.model
    # def _get_default_country(self):
    #     country = self.env['res.country'].search([('code', '=', 'US')], limit=1)
    #     return country
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)

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

    #Notes Tab
    note_group = fields.Integer('Note Group')
    note_type = fields.Selection([],'Type')
    display_repeats = fields.Selection([], 'Display Repeats')
    print_repeats = fields.Selection([], 'Print Repeats')
    message = fields.Text('Message')

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
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'US')], limit=1)
        return country
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

    filter_by_vname = fields.Many2one('wgd.vendors')
    filter_by_vid = fields.Many2one('wgd.vendors')
    
    ########################## CUSTOMER FIELDS ###########################

    customer_id             = fields.Char("Customer ID",help='Exportable')
    job_ids                  = fields.Many2one('wgd.job.no')
    has_job                 = fields.Selection([('Y','Y'),('N','N')], "Has Job?",help='Exportable')
    sort_name_id            = fields.Char("Sort",help='Exportable')
    bill_to_id              = fields.Many2one('res.partner')
    ace_rewards             = fields.Char("Ace Rewards",help='Exportable')
    filter_by_name          = fields.Many2one('res.partner')
    filter_by_id            = fields.Many2one('res.partner')

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
    terms_code              = fields.Many2one('account.payment.term', 'Terms Code')
    category_plan_id        = fields.Many2one('category')
    tax_code                = fields.Selection([('yes','Y'),('no','N')], "Tax Code", default='yes',help='Exportable')
    salesperson             = fields.Selection([('yes','Y'),('no','N')], "Salesperson", default='no',help='Exportable')
    pure_archive_invoices   = fields.Char('Pure Archive Invoices',help='Exportable')
    po_required             = fields.Selection([('yes','Y'),('no','N')], "PO Required", default='no',help='Exportable')
    default_po              = fields.Char('Default PO',help='Exportable')
    charge_allowed          = fields.Selection([('yes','Y'),('no','N')], "Charge Allowed", default='yes',help='Exportable')
    balance_method          = fields.Many2one('balance',default=lambda self: self.env['balance'].search([('name','=','O')]), limit=1)
    std_sell_price          = fields.Selection([('yes','R'),('no','R')], "Std Sell Price/POS", default='no',help='Exportable')
    finace_charges          = fields.Monetary(string="Finace Charges")
    store_acct_opened_id    = fields.Many2one('res.company')
    transfer_to_store       = fields.Selection([('yes','Y'),('no','N')], "Transfer To Store", default='no',help='Exportable')
    print_statments         = fields.Selection([('yes','Y'),('no','N')], "Print Statments", default='no')
    check_allowed           = fields.Selection([('yes','Y'),('no','N')], "Check Allowed", default='no',help='Exportable')
    credit_are_only         = fields.Selection([('yes','Y'),('no','N')], "Credit A/R Only", default='no',help='Exportable')
    taxable                 = fields.Selection([('yes','Y'),('no','N')], "Taxable", default='no')
    keep_dept_history       = fields.Selection([('yes','Y'),('no','N')], "Keep Dept History", default='yes',help='Exportable')
    print_invoices_in_pos   = fields.Selection([('yes','Y'),('no','N')], "Print Invoices In POS", default='no',help='Exportable')
    last_activity_date      = fields.Date("Last Activity Date")

    # notebook page2 Credit
    finace_chgs_ytd         = fields.Float("Finace Chgs YTD", digits=(2,2))
    higest_acc_balance      = fields.Float("Higest Acct Balance")
    credit_available        = fields.Float("Credit Available",compute="_total_credit") 
    running_balance         = fields.Float("Running Balance",compute="_total_running_bal")
    statment_balance        = fields.Float("Statment Balance",compute="_total_stmt_bal")
    statment_discount       = fields.Float("Statment Discount")
    returns                 = fields.Float("Returns",compute="_total_refund")
    transations             = fields.Float("Transations",compute="_total_invoices")
    declining_credit_limit  = fields.Selection([('yes','Y'),('no','N')], "Declining Credit Limit", default='yes',help='Exportable')
    global_credit_check     = fields.Selection([('yes','Y'),('no','N')], "Global Credit Check", default='no',help='Exportable')
    order_bal_credit_avail  = fields.Selection([('yes','Y'),('no','N')], "Use Order Bal in Credit Avail", default='no',help='Exportable')
    last_sale               = fields.Date("Last Sale")
    acct_opened             = fields.Date("Acct Opened")
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
    credit_ids              = fields.One2many('credit', 'customer_id',string=" ")  
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
    default_price_uom       = fields.Many2one('uom.uom')
    statment_by_job         = fields.Selection([('s','S')], "Statment By Job", default='s',help='Exportable')
    additional_flag          = fields.Char('Additional Flags',help='Exportable')    
    names_ids              = fields.One2many('names', 'customer_id',string=" ") 

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

    # def name_get(self): 
    #     result = [] 
    #     for rec in self:
    #         if self.env.context.get('hide_code'):
    #             name = rec.name
    #         else:
    #             name = rec.customer_id
    #         result.append((rec.id, name))
    #     return result

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('hide_code'):
                name = rec.name
            else:
                if rec.customer_id:
                    name = rec.customer_id
                else:
                    name = rec.name
            result.append((rec.id, name))
        return result
        
    @api.onchange('filter_by_name')
    def onchange_name(self):
        '''
            Auto fill the customer data on the all fields based on selected customer name 
        '''
        if self.filter_by_name:
            customer_name = self.search([('name', '=', self.filter_by_name.name)], limit=1)
            if customer_name:
                self.filter_by_id   =""
                self.street         = customer_name.street
                self.street2        = customer_name.street2
                self.city           = customer_name.city
                self.state_id       = customer_name.state_id
                self.zip            = customer_name.zip
                self.country_id     = customer_name.country_id
                self.phone          = customer_name.phone
                self.fax            = customer_name.fax
                self.contact        = customer_name.contact
                self.country_id     = customer_name.country_id
                self.credit_message1= customer_name.credit_message1
                self.credit_message2= customer_name.credit_message2
                self.credit_limit   = customer_name.credit_limit
                self.trade_discount = customer_name.trade_discount
                self.account_code1  = customer_name.account_code1
                self.monthly_payment= customer_name.monthly_payment
                self.terms_code     = customer_name.terms_code
                self.category_plan_id= customer_name.category_plan_id
                self.tax_code       = customer_name.tax_code
                self.salesperson    = customer_name.salesperson
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
                self.job_ids= customer_name.job_ids
                self.has_job= customer_name.has_job
                self.sort_name_id= customer_name.sort_name_id
                self.bill_to_id= customer_name.bill_to_id
                self.ace_rewards= customer_name.ace_rewards
                self.name= customer_name.name

                self.finace_chgs_ytd= customer_name.finace_chgs_ytd
                self.higest_acc_balance= customer_name.higest_acc_balance
                self.credit_available= customer_name.credit_available
                self.running_balance= customer_name.running_balance
                self.statment_balance= customer_name.statment_balance
                self.statment_discount= customer_name.statment_discount
                self.returns= customer_name.returns
                self.transations= customer_name.transations
                self.declining_credit_limit= customer_name.declining_credit_limit
                self.global_credit_check= customer_name.global_credit_check
                self.order_bal_credit_avail= customer_name.order_bal_credit_avail
                self.acct_opened= customer_name.acct_opened
                self.monthly_payment= customer_name.monthly_payment
                self.lyr_fin_charge= customer_name.lyr_fin_charge
                self.date_last_pay= customer_name.date_last_pay
                self.amount_last_pay= customer_name.amount_last_pay
                self.special_charges= customer_name.special_charges

                self.store= customer_name.store
                self.std_sell_prices= customer_name.std_sell_prices
                self.delete_all= customer_name.delete_all
                self.customer_sales_summary= customer_name.customer_sales_summary
                self.credit_ids= customer_name.credit_ids
                self.period_to_date_sale= customer_name.period_to_date_sale
                self.period_to_date_cost= customer_name.period_to_date_cost
                self.period_to_date_gp= customer_name.period_to_date_gp
                self.year_to_date_sale= customer_name.year_to_date_sale
                self.year_to_date_cost= customer_name.year_to_date_cost
                self.year_to_date_gp= customer_name.year_to_date_gp
                self.last_year_sale= customer_name.last_year_sale
                self.last_year_cost= customer_name.last_year_cost
                self.last_year_gp= customer_name.last_year_gp

                self.period_to_date_gp_dollor= customer_name.period_to_date_gp_dollor
                self.year_to_date__dollor= customer_name.year_to_date__dollor
                self.last_year_gp_dollor= customer_name.last_year_gp_dollor
                self.terms_disc= customer_name.terms_disc
                self.year_to_date_fin_chrgs= customer_name.year_to_date_fin_chrgs
                self.last_year_gp_fin_chrgs= customer_name.last_year_gp_fin_chrgs
                self.year_to_date_returns= customer_name.year_to_date_returns
                self.year_to_date_transaction= customer_name.year_to_date_transaction
                self.customer_sales_summary= customer_name.customer_sales_summary

                self.of_times_no_activity= customer_name.of_times_no_activity
                self.of_times_current= customer_name.of_times_current
                self.of_times_1_30= customer_name.of_times_1_30
                self.of_times_31_60= customer_name.of_times_31_60
                self.of_times_61_90= customer_name.of_times_61_90
                self.of_times_over_90= customer_name.of_times_over_90
                self.last_occured_no_activity= customer_name.last_occured_no_activity
                self.last_occured_current= customer_name.last_occured_current
                self.last_occured_1_30= customer_name.last_occured_1_30
                self.last_occured_31_60= customer_name.last_occured_31_60
                self.last_occured_61_90= customer_name.last_occured_61_90
                self.last_occured_over_90= customer_name.last_occured_over_90

                self.social_security= customer_name.social_security
                self.birth_date= customer_name.birth_date
                self.pst_registration= customer_name.pst_registration
                self.gst_registration= customer_name.gst_registration
                self.pesticide_license= customer_name.pesticide_license
                self.pesticide_lic_exp= customer_name.pesticide_lic_exp
                self.freght_factor= customer_name.freght_factor
                self.rescale_code= customer_name.rescale_code
                self.alternate_phone= customer_name.alternate_phone
                self.alternate_fax= customer_name.alternate_fax
                self.open_quote_1= customer_name.open_quote_1
                self.open_quote_2= customer_name.open_quote_2
                self.rebate_plan= customer_name.rebate_plan
                self.business_type= customer_name.business_type
                self.location= customer_name.location
                self.customer_ranks= customer_name.customer_ranks
                self.statment_type= customer_name.statment_type
                self.statment_fmt= customer_name.statment_fmt
                self.statment_fmt2= customer_name.statment_fmt2
                self.Invoice_credit= customer_name.Invoice_credit
                self.order_sp_ord_estimate= customer_name.order_sp_ord_estimate
                self.fax_pos_stmt= customer_name.fax_pos_stmt
                self.fax_pos_stmt1= customer_name.fax_pos_stmt1
                self.ace_rewards_status= customer_name.ace_rewards_status
                self.tax_override_plan= customer_name.tax_override_plan
                self.prompt_in_pos= customer_name.prompt_in_pos
                self.prompt_threshold= customer_name.prompt_threshold
                self.price_pick_ticket= customer_name.price_pick_ticket
                self.open_quotes= customer_name.open_quotes
                self.global_credit_check= customer_name.global_credit_check
                self.print_lumber_totals= customer_name.print_lumber_totals
                self.default_price_uom= customer_name.default_price_uom
                self.statment_by_job= customer_name.statment_by_job
                self.additional_flag= customer_name.additional_flag
                self.names_ids= customer_name.names_ids

                self.current_total= customer_name.current_total
                self.thirty_total= customer_name.thirty_total
                self.sixty_total= customer_name.sixty_total
                self.ninety_total= customer_name.ninety_total
                self.over_total= customer_name.over_total
                self.message= customer_name.message


    @api.onchange('filter_by_id')
    def onchange_id(self):       
        '''
            Auto fill the customer data on the all fields based on selected customer ID 
        '''
        if self.filter_by_id:
            customer_id = self.search([('customer_id', '=', self.filter_by_id.customer_id)], limit=1)
            if customer_id:
                self.filter_by_name   =""
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
                self.job_ids= customer_id.job_ids
                self.has_job= customer_id.has_job
                self.sort_name_id= customer_id.sort_name_id
                self.bill_to_id= customer_id.bill_to_id
                self.ace_rewards= customer_id.ace_rewards
                self.name= customer_id.name

                self.finace_chgs_ytd= customer_id.finace_chgs_ytd
                self.higest_acc_balance= customer_id.higest_acc_balance
                self.credit_available= customer_id.credit_available
                self.running_balance= customer_id.running_balance
                self.statment_balance= customer_id.statment_balance
                self.statment_discount= customer_id.statment_discount
                self.returns= customer_id.returns
                self.transations= customer_id.transations
                self.declining_credit_limit= customer_id.declining_credit_limit
                self.global_credit_check= customer_id.global_credit_check
                self.order_bal_credit_avail= customer_id.order_bal_credit_avail
                self.acct_opened= customer_id.acct_opened
                self.monthly_payment= customer_id.monthly_payment
                self.lyr_fin_charge= customer_id.lyr_fin_charge
                self.date_last_pay= customer_id.date_last_pay
                self.amount_last_pay= customer_id.amount_last_pay
                self.special_charges= customer_id.special_charges

                self.store= customer_id.store
                self.std_sell_prices= customer_id.std_sell_prices
                self.delete_all= customer_id.delete_all
                self.customer_sales_summary= customer_id.customer_sales_summary
                self.credit_ids= customer_id.credit_ids
                self.period_to_date_sale= customer_id.period_to_date_sale
                self.period_to_date_cost= customer_id.period_to_date_cost
                self.period_to_date_gp= customer_id.period_to_date_gp
                self.year_to_date_sale= customer_id.year_to_date_sale
                self.year_to_date_cost= customer_id.year_to_date_cost
                self.year_to_date_gp= customer_id.year_to_date_gp
                self.last_year_sale= customer_id.last_year_sale
                self.last_year_cost= customer_id.last_year_cost
                self.last_year_gp= customer_id.last_year_gp

                self.period_to_date_gp_dollor= customer_id.period_to_date_gp_dollor
                self.year_to_date__dollor= customer_id.year_to_date__dollor
                self.last_year_gp_dollor= customer_id.last_year_gp_dollor
                self.terms_disc= customer_id.terms_disc
                self.year_to_date_fin_chrgs= customer_id.year_to_date_fin_chrgs
                self.last_year_gp_fin_chrgs= customer_id.last_year_gp_fin_chrgs
                self.year_to_date_returns= customer_id.year_to_date_returns
                self.year_to_date_transaction= customer_id.year_to_date_transaction
                self.customer_sales_summary= customer_id.customer_sales_summary

                self.of_times_no_activity= customer_id.of_times_no_activity
                self.of_times_current= customer_id.of_times_current
                self.of_times_1_30= customer_id.of_times_1_30
                self.of_times_31_60= customer_id.of_times_31_60
                self.of_times_61_90= customer_id.of_times_61_90
                self.of_times_over_90= customer_id.of_times_over_90
                self.last_occured_no_activity= customer_id.last_occured_no_activity
                self.last_occured_current= customer_id.last_occured_current
                self.last_occured_1_30= customer_id.last_occured_1_30
                self.last_occured_31_60= customer_id.last_occured_31_60
                self.last_occured_61_90= customer_id.last_occured_61_90
                self.last_occured_over_90= customer_id.last_occured_over_90

                self.social_security= customer_id.social_security
                self.birth_date= customer_id.birth_date
                self.pst_registration= customer_id.pst_registration
                self.gst_registration= customer_id.gst_registration
                self.pesticide_license= customer_id.pesticide_license
                self.pesticide_lic_exp= customer_id.pesticide_lic_exp
                self.freght_factor= customer_id.freght_factor
                self.rescale_code= customer_id.rescale_code
                self.alternate_phone= customer_id.alternate_phone
                self.alternate_fax= customer_id.alternate_fax
                self.open_quote_1= customer_id.open_quote_1
                self.open_quote_2= customer_id.open_quote_2
                self.rebate_plan= customer_id.rebate_plan
                self.business_type= customer_id.business_type
                self.location= customer_id.location
                self.customer_ranks= customer_id.customer_ranks
                self.statment_type= customer_id.statment_type
                self.statment_fmt= customer_id.statment_fmt
                self.statment_fmt2= customer_id.statment_fmt2
                self.Invoice_credit= customer_id.Invoice_credit
                self.order_sp_ord_estimate= customer_id.order_sp_ord_estimate
                self.fax_pos_stmt= customer_id.fax_pos_stmt
                self.fax_pos_stmt1= customer_id.fax_pos_stmt1
                self.ace_rewards_status= customer_id.ace_rewards_status
                self.tax_override_plan= customer_id.tax_override_plan
                self.prompt_in_pos= customer_id.prompt_in_pos
                self.prompt_threshold= customer_id.prompt_threshold
                self.price_pick_ticket= customer_id.price_pick_ticket
                self.open_quotes= customer_id.open_quotes
                self.global_credit_check= customer_id.global_credit_check
                self.print_lumber_totals= customer_id.print_lumber_totals
                self.default_price_uom= customer_id.default_price_uom
                self.statment_by_job= customer_id.statment_by_job
                self.additional_flag= customer_id.additional_flag
                self.names_ids= customer_id.names_ids

                self.current_total= customer_id.current_total
                self.thirty_total= customer_id.thirty_total
                self.sixty_total= customer_id.sixty_total
                self.ninety_total= customer_id.ninety_total
                self.over_total= customer_id.over_total
                self.message= customer_id.message
    
    @api.depends('current_total','thirty_total','sixty_total','ninety_total','over_total')
    def _smart_button(self):
        '''
            Fetch invoice details from aged recivable 
        '''
        current_date    = date.today()
        customer_invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),('partner_id', '=', self.id),('state', '=', 'posted'),('invoice_date', '<=', current_date)])
        refund__invoices  = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.id),('state', '=', 'posted'),('invoice_date', '<=', current_date)])
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

    # @api.model    
    # def create(self, vals):
    #     '''
    #      Search customer id only, need to check company id also after working on res,.partner and csv
    #     '''
    #     if 'customer_id' in vals :  
    #         cus_dup = self.env['my.customer'].search([('customer_id','=',vals['customer_id'])], limit=1) 
    #         if len(cus_dup) > 0:
    #             raise ValidationError(f'Customer ID ({cus_dup.customer_id}) already exists')
    #         res = super(Customer, self).create(vals)
    #         return res

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

    @api.depends('statment_balance')
    def _total_stmt_bal(self):
        '''
            Statment Balance =  sum of  journals debit sum - sum of journals credit sum
        '''
        
        invoices_recivable = self.env['account.move.line'].search([('account_id', '=', '121000 Account Receivable'),('partner_id', '=', self.id)])
        invoices_payable   = self.env['account.move.line'].search([('account_id', '=', '211000 Account Payable'),('partner_id', '=', self.id)])
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

        invoices_recivable = self.env['account.move.line'].search([('account_id', '=', '121000 Account Receivable'),('partner_id', '=', self.id),('parent_state', '=', 'posted')])
        invoices_payable   = self.env['account.move.line'].search([('account_id', '=', '211000 Account Payable'),('partner_id', '=', self.id),('parent_state', '=', 'posted')])
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
        invoices = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.id)])
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
        invoices = self.env['account.move'].search([('invoice_date', '>', date),('move_type', '=', 'out_invoice'),('partner_id', '=', self.id)])
        self.transations = len(invoices)

    @api.depends('credit_limit')
    def _total_credit(self):
        '''
            Credit available = credit limit - sum of invoices due amount
        '''
        invoices = self.env['account.move'].search([('move_type', '=', 'out_refund'),('partner_id', '=', self.id)])
        total = 0
        for record in invoices:
            total = total + record.amount_residual
        for record in self:
            credit_limits = record.credit_limit
        self.credit_available = float(credit_limits) - float(total)
    
    @api.onchange('is_customer_vendor')
    def onchange_customer(self):
        if self.is_customer_vendor == 'is_customer':
            self.supplier_rank = 0
            self.customer_rank = 1
        else:
            self.supplier_rank = 1
            self.customer_rank = 0