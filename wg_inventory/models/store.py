from odoo import models, fields, api

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
    

class AccountTaxInherited(models.Model):
    """Inherited base account.tax model and added store field """
    _inherit = "account.tax"

    store = fields.Many2one('wg.store', name="Store")
    pos_session = fields.Many2one('pos.config')

class HrEmployeeInherited(models.Model):
    """Inherited base hr.employee model and added store field """
    _inherit = "hr.employee"

    store = fields.Many2one('wg.store', name="Store")



