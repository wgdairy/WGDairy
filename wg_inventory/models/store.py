from odoo import models, fields, api
import re

class StoreLocation(models.Model):
    """Model for adding WG Dairy Stores"""
    _name = "wg.store"
    _description = "WG Dairy Stores"

    name = fields.Char('Store')
    warehouse = fields.Many2one('stock.warehouse')
    long_name = fields.Char('Long Name')
    street = fields.Char('Street')
    street2 = fields.Char('Street 2')
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')

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
            self.fax = start_group

class AccountTaxInherited(models.Model):
    """Inherited base account.tax model and added store field """
    _inherit = "account.tax"

    store = fields.Many2one('wg.store', name="Store")
    pos_session = fields.Many2one('pos.config')

class HrEmployeeInherited(models.Model):
    """Inherited base hr.employee model and added store field """
    _inherit = "hr.employee"

    store = fields.Many2one('wg.store', name="Store")



