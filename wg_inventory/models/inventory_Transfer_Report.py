# Inventory_Transfer _Report
from odoo import models, fields, api

# class Inventory_Rep(models.Model):
#     _name = 'inventory_report'
#
#     cust_no = fields.Char()
#     job_no = fields.Char()
#     purchase_order = fields.Char()
#     reference = fields.Char()
#     terms = fields.Char()
#     clerk = fields.Char()
#     date_time = fields.Date()
#     sold_to = fields.Date()
#     ship_to = fields.Char()
#     del_date = fields.Date()
#     terminal = fields.Char()
#     order = fields.Char()
#     tax = fields.Char()
#     complete = fields.Char()
#     #line
#     shipped = fields.Char()
#     ordered = fields.Char()
#     um = fields.Char()
#     sku = fields.Char()
#     description = fields.Char()
#     location = fields.Char()
#     unit = fields.Char()
#     price = fields.Char()
#     unit = fields.Char()
#     price = fields.Float()
#     extension = fields.Char()
#     taxable = fields.Float()
#     non_taxable = fields.Float()
#     sub_total = fields.Float()  purchase.order  account.tax

# Inventory_Transfer _Report
from odoo import models, fields, api

class Inventory_Rep(models.Model):
    # _name = 'inventory_report'
    _inherit = "stock.picking"

    cust_no = fields.Many2one('res.partner',ondelete='restrict', index=True,) #error
    job_nos = fields.Char()
    purchase_order = fields.Char() #erreo
    reference = fields.Char()
    terms = fields.Many2one('account.payment.term',ondelete='restrict', index=True,)
    clerk = fields.Many2one('hr.employee',ondelete='restrict', index=True,)
    date_time = fields.Datetime()
    sold_to = fields.Char()
    ship_to = fields.Char()
    del_date = fields.Date()
    terminal = fields.Char()
    order = fields.Many2one('purchase.order',ondelete='restrict', index=True,)
    tax = fields.Many2one('account.tax',ondelete='restrict', index=True,)
    complete = fields.Char()
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        check_company=True,required=True, readonly=False)
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        check_company=True, required=True,readonly=False)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=False)
    taxable = fields.Float(digits = (12,2))
    non_taxable = fields.Float(digits = (12,2))
    sub_total = fields.Float(digits = (12,2))
    #line
    report_lines = fields.One2many('stock.move.line', 'inventoryReport')



class InventoryReportLines(models.Model):
    # _name = 'inventory.report.lines'
    _inherit = "stock.move.line"
    inventoryReport = fields.Many2one('stock.picking')
    line = fields.Integer()
    shipped = fields.Float(digits = (12,2))
    ordered = fields.Float(digits = (12,2))
    um = fields.Char()
    sku = fields.Char()
    description = fields.Char()
    location = fields.Char()
    unit = fields.Char()
    price = fields.Float(digits = (12,2))
    extension = fields.Float(digits = (12,2))
    location_id = fields.Many2one('stock.location', 'From', domain="[('usage', '!=', 'view')]", check_company=True, required=True)
    location_dest_id = fields.Many2one('stock.location', 'To', domain="[('usage', '!=', 'view')]", check_company=True, required=True)
    # currency_id = fields.Many2one("res.currency")

    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=False, index=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=False,
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_qty = fields.Float('Reserved', default=0.0, digits='Product Unit of Measure', required=False, copy=False)

class Inventory_Repeee(models.Model):
    _name = 'inventory_report'

class InventoryReportLines(models.Model):
    _name = 'inventory.report.lines'

    # prices = fields.Monetary(currency_field='currency_id')
    # extensions = fields.Monetary(currency_field='currency_id')
    # currency_id = fields.Many2one("res.currency")
    # class LibraryBook(models.Model):
    #     # ...
    #     retail_price = fields.Monetary(
    #         'Retail Price',
    #         # optional: currency_field='currency_id',
    #         ...
    #
    # class Inventory_Rep(models.Model):
    #     _name = 'inventory_report'
    #
    #     cust_no = fields.Char()
    #     job_no = fields.Char()
    #     purchase_order = fields.Char()
    #     reference = fields.Char()
    #     terms = fields.Char()
    #     clerk = fields.Char()
    #     date_time = fields.Datetime()
    #     sold_to = fields.Date()
    #     ship_to = fields.Char()
    #     del_date = fields.Date()
    #     terminal = fields.Char()
    #     order = fields.Char()
    #     tax = fields.Char()
    #     complete = fields.Char()
    #     taxable = fields.Float()
    #     non_taxable = fields.Float()
    #     sub_total = fields.Float()
    #     # line
    #     report_lines = fields.One2many('inventory.report.lines', 'inventoryReport')
    #
    # class InventoryReportLines(models.Model):
    #     _name = 'inventory.report.lines'
    #
    #     inventoryReport = fields.Many2one('inventory_report')
    #     line = fields.Integer()
    #     shipped = fields.Float()
    #     ordered = fields.Float()
    #     um = fields.Char()
    #     sku = fields.Char()
    #     description = fields.Char()
    #     location = fields.Char()
    #     unit = fields.Char()
    #     prices = fields.Float()
    #     extensions = fields.Float()