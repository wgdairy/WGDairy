# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wg_po(models.Model):
    _inherit = "purchase.order"


    Store_ids = fields.Many2one('res.company', ondelete='restrict', index=True, )
    # BkOrd = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    BkOrds = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    Total_Stk_Units = fields.Char(string='Total Stk Units')
    Total_Cost = fields.Char(string='Total Cost')
    Total_Weight = fields.Char(string='Total Weight')
    # pur_order_line = fields.Many2one('product.template',ondelete='restrict', index=True,)
    pur_order_lines = fields.One2many('purchase.order.line', 'pur_ids', string="Trips and Tolls")
    Date_Created = fields.Date()
    Reference = fields.Char()
    Alt_po = fields.Char(string="Alt PO")
    Order_Type = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    Buyerid = fields.Char(string="Buyer's ID")
    Special_Instructions = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    Line_Items = fields.Char()
    ven_street = fields.Char()
    ven_street2 = fields.Char()
    ven_city = fields.Char()
    ven_state_id = fields.Char()
    ven_zip = fields.Char()
    ven_country_id = fields.Many2one("res.country", help='Exportable')
    ven_state = fields.Many2one("res.country.state", ondelete='restrict', help='Exportable')
    ven_phone = fields.Char()
    ven_fax = fields.Char()

    ship_street = fields.Char()
    ship_street2 = fields.Char()
    ship_city = fields.Char()
    ship_state_id = fields.Many2one("res.country.state", ondelete='restrict',  help='Exportable')
    ship_zip = fields.Char()
    ship_country_id = fields.Many2one("res.country",  help='Exportable')
    Total_Freight = fields.Char()
    Other_Charges = fields.Char()

    # change the string Date Planned to Due Date
    date_planned = fields.Datetime(
        string='Due date', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

    @api.onchange('partner_id')
    def _onchange_sku(self):

        onc_ve_fa = self.env['wgd.vendors'].search(
            [ ('partner_id', '=', self.partner_id.id)])
        onc_vend = self.env['res.partner'].search(
            [('name', '=', self.partner_id.name), ('id', '=', self.partner_id.id)])

        self.ven_street = onc_vend.street
        self.ven_street2 = onc_vend.street2
        self.ven_city = onc_vend.city
        self.ven_state_id = onc_vend.state_id
        self.ven_zip = onc_vend.zip
        self.ven_country_id = onc_vend.country_id
        self.ven_phone = onc_ve_fa.phone
        self.ven_fax = onc_ve_fa.fax
        self.Store_ids = onc_ve_fa.company_id


class wg_po(models.Model):
    _inherit = "purchase.order.line"

    Popularity_Code = fields.Char(string='Popularity Code')
    OM = fields.Char()
    Ext_Cost = fields.Float('Ext Cost')
    UM_Pur = fields.Float('UM(Pur)')
    PO_Season = fields.Char(string='PO Season')
    ROP_Product = fields.Char(string='ROP Product')
    Last_12_Units = fields.Char(string='Last 12 Units')
    pur_ids = fields.Many2one('purchase.order')
    # sku_id = fields.Many2one('product.template',ondelete='restrict', index=True,)
    mfg = fields.Char()
    # desc = fields.Char()
    qty_available = fields.Float()
    # product_qty = fields.Float()
    list_price = fields.Float()
    load_retail = fields.Float()
    order_point = fields.Float()
    UM_Pur = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    min_op = fields.Float()
    max_stock_level = fields.Float()
    Safety_Stock = fields.Float()
    dept = fields.Many2one('hr.department', ondelete='restrict', index=True, )
    location_id = fields.Char()
    ln =  fields.Integer(compute='_get_line_numbers', string='Serial Number',readonly=False, default=False)

    
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.order_id.order_line:
                line_rec.ln = line_num
                line_num += 1



    @api.onchange('product_id')
    def _onchange_sku(self):
        onc_sku = self.env['product.template'].search([('name', '=', self.product_id.name), ('id', '=', self.product_id.product_tmpl_id.id)])

        self.qty_available = onc_sku.qty_available
        self.price_unit = onc_sku.list_price
        self.dept = onc_sku.deptart









