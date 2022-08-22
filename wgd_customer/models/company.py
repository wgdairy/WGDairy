from odoo import models
from odoo import api, fields, models, SUPERUSER_ID, _

class res_company(models.Model):


    _inherit = 'res.company'
    _description = 'company_inherit_model'

    fax = fields.Char(string="Fax")