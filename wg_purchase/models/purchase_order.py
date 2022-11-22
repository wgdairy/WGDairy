# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import datetime


class wg_po(models.Model):
    _inherit = "purchase.order"

    Store_ids = fields.Many2one('res.company', ondelete='restrict', index=True, )
    # BkOrd = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    BkOrds = fields.Selection([('Y', 'Y'), ('N', 'N'), ],compute='_bak_order')
    # BkOrds = fields.Char(comput='_bak_order')
    Total_Stk_Units = fields.Char(string='Total Stk Units',compute='_cal_stk_unit',readonly=True)
    Total_Cost = fields.Char(string='Total Cost',compute='_cal_tot_cost',readonly=True)
    Total_Weight = fields.Char(string='Total Weight',compute='_cal_tot_weight',readonly=True)
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
    ven_state_ids = fields.Many2one("res.country.state", ondelete='restrict', help='Exportable')
    ven_phone = fields.Char()
    ven_fax = fields.Char()

    ship_street = fields.Char()
    ship_street2 = fields.Char()
    ship_city = fields.Char()
    ship_state_id = fields.Many2one("res.country.state", ondelete='restrict', help='Exportable')
    ship_zip = fields.Char()
    ship_country_id = fields.Many2one("res.country", help='Exportable')
    Total_Freight = fields.Char()
    Other_Charges = fields.Char()
    Date_send = fields.Datetime()

    # change the string Date Planned to Due Date
    date_planned = fields.Datetime(
        string='Due date', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default, show the date and time of mail send in Date send field.
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase')[2]
            else:
                template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase_done')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'active_model': 'purchase.order',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = _('Request for Quotation')
        else:
            ctx['model_description'] = _('Purchase Order')

        self.Date_send = datetime.datetime.today().strftime('%Y-%m-%d')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('partner_id')
    def _onchange_sku(self):

        '''
        This function auto populate the address,phone and fax of vendor selected in purchase order.
        '''

        # onc_ve_fa = self.env['wgd.vendors'].search(
        #     [('partner_id', '=', self.partner_id.id)])
        onc_vend = self.env['res.partner'].search(
            [('name', '=', self.partner_id.name), ('id', '=', self.partner_id.id)])

        self.ven_street = onc_vend.street
        self.ven_street2 = onc_vend.street2
        self.ven_city = onc_vend.city
        self.ven_state_ids = onc_vend.state_id.id
        self.ven_zip = onc_vend.zip
        self.ven_country_id = onc_vend.state_id.country_id.id
        self.ven_phone = onc_vend.phone
        self.ven_fax = onc_vend.fax
        self.Store_ids = onc_vend.company_id


    def _bak_order(self):
        '''
        This function check the back order,if any back order show in BkOrds field.
        '''

        bk_orders = self.env['stock.picking'].search([('origin', '=', self.name), ('company_id', '=', self.company_id.id),('state', '!=', 'done')],limit=1)
      


        if bk_orders:

            if bk_orders.backorder_id and bk_orders.state != 'done':

                self.BkOrds = 'Y'
            else:
                self.BkOrds = 'N'
        else:
            self.BkOrds = 'N'






    def _cal_tot_cost(self):
        '''
         Function to calculate the total cost.Total cost is sum of all price unit in products.
        '''
        tot_cost = 0
        for rec in self.order_line:
            tot_cost += rec.price_unit
        self.Total_Cost = str(tot_cost)

    def _cal_stk_unit(self):
        '''
         Function to calculate the total stock unit.Total stock unit is sum of all stock in products.
        '''
        tot_stk = 0
        for rec in self.order_line:
            tot_stk += rec.qty_available
        self.Total_Stk_Units = str(tot_stk)



    def _cal_tot_weight(self):
        '''
         Function to calculate the total Weight unit.Total Weight is sum of all weight in products.
        '''
        tot_weight = 0
        for rec in self.order_line:
            tot_weight += rec.product_id.product_tmpl_id.weight
        self.Total_Weight = str(tot_weight)


class wg_po(models.Model):
    _inherit = "purchase.order.line"

    Popularity_Code = fields.Char(string='Popularity Code')
    OM = fields.Char()
    Ext_Cost = fields.Float('Ext Cost',compute='_compute_extcost')
    UM_Pur = fields.Float('UM(Pur)')
    cost_stk = fields.Float('Cost(Stk)',compute='_get_cost_stk',readonly=False,store=True)
    PO_Season = fields.Char(string='PO Season')
    ROP_Product = fields.Char(string='ROP Product')
    Last_12_Units = fields.Char(string='Last 12 Units')
    pur_ids = fields.Many2one('purchase.order')
    # sku_id = fields.Many2one('product.template',ondelete='restrict', index=True,)
    mfg = fields.Char()
    # desc = fields.Char()
    qty_available = fields.Float()
    # product_qty = fields.Float()
    # list_price = fields.Float()
    load_retail = fields.Float(related='product_id.product_tmpl_id.reail',readonly=False,)
    order_point = fields.Float(related='product_id.product_tmpl_id.order_point')
    UM_Pur = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    min_op = fields.Float(related='product_id.product_tmpl_id.reordering_min_qty')
    max_stock_level = fields.Float(related='product_id.product_tmpl_id.reordering_max_qty')
    Safety_Stock = fields.Float(related='product_id.product_tmpl_id.safety_stock')
    dept = fields.Many2one('hr.department', ondelete='restrict', index=True, )
    location_id = fields.Char()
    ln = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price',related='product_id.product_tmpl_id.list_price' )
    desc_sku = fields.Char(related='product_id.product_tmpl_id.name', string='Description', readonly=False)

    def _get_line_numbers(self):
        '''
            Function to Generate line number in purchase order line.
        '''
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.order_id.order_line:
                line_rec.ln = line_num
                line_num += 1

    @api.onchange('product_id')
    def _get_cost_stk(self):

        '''
         Function to auto populate the cost(stk).Get cost from produt
        '''
        for rec in self:

            onc_cost = self.env['product.template'].search(
            [('name', '=', rec.product_id.name), ('id', '=', rec.product_id.product_tmpl_id.id)],limit=1)

            # rec.cost_stk = onc_cost.list
            rec.cost_stk = onc_cost.avg_cost_pricing


    @api.onchange('product_id')
    def _onchange_skus(self):
        '''
                 Function to auto populate the quantity,department,unit prie.
        '''
        onc_sku = self.env['product.template'].search(
            [('name', '=', self.product_id.name), ('id', '=', self.product_id.product_tmpl_id.id)])


        self.qty_available = onc_sku.qty_available
        self.dept = onc_sku.deptart
        self.price_unit = onc_sku.list_price

        res = {}
        if onc_sku:
            if self.partner_id != onc_sku.prime_vede :
                if self.partner_id != onc_sku.mfg_vende:
                    res = {'warning': {'title': _('Warning'),'message': _('Product not related to vendor.')}}
            elif self.partner_id != onc_sku.mfg_vende:
                if self.partner_id != onc_sku.prime_vede:
                    res = {'warning': {'title': _('Warning'),'message': _('Product not related to vendor.')}}
        if res:
            return res

    @api.depends('product_qty','cost_stk')
    def _compute_extcost(self):
        '''
            Function to calculate the ext cost.
        '''
        ex_cost = 0
        for rec in self:

            ex_cost = rec.product_qty * rec.cost_stk
            rec.Ext_Cost = float(ex_cost)

class InheritMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self,vals):
        res = super(InheritMove, self).create(vals)
        if res.release_to_pay_manual:
            if res.release_to_pay_manual == 'exception' or res.release_to_pay_manual == 'no':
                raise ValidationError('Vendor Bill and PO do not match')
        return res










