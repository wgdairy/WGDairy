from odoo import models, fields, api
from odoo.exceptions import ValidationError


class wg_task(models.Model):
    _inherit = "project.task"

    stock_mic_ids = fields.One2many('stock.misc', 'job_stock_id', string='Stock')


# Stock/Misc model

class stock_misc(models.Model):
    _name = 'stock.misc'

    sku_id = fields.Many2one('product.template',ondelete='restrict', index=True,)
    Description = fields.Char()
    Unit_Price = fields.Float()
    Ext_Price = fields.Float(compute='cal_ext_price')
    qty = fields.Float()
    job_stock_id = fields.Many2one('project.task', index=1)


    @api.onchange('sku_id')
    def onchange_skus(self):
        for record in self:
            skus = self.env['product.template'].search([('id', '=', record.sku_id.id),('name', '=', record.sku_id.name)], limit=1)
            record.Description = skus.desc
            record.Unit_Price = skus.list_price


    @api.depends('qty', 'Unit_Price')
    def cal_ext_price(self):
        for record in self:
            record.Ext_Price = record.qty * record.Unit_Price

    @api.onchange('qty')
    def validate_qty(self):
        if self.qty:
            if len(str(self.qty)) > 7:
                raise ValidationError("5 digits be allowed in qty")
    @api.onchange('Unit_Price')
    def validate_Unit_Price(self):
        if self.Unit_Price:
            if len(str(self.Unit_Price)) > 12:
                raise ValidationError("10 digits be allowed in Unit_Price")




