# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from itertools import groupby
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import AccessError, UserError, ValidationError

import datetime


class wg_po(models.Model):
    _inherit = "purchase.order"

    vendor_code = fields.Char()
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
    Other_Charges = fields.Float()
    Date_send = fields.Datetime()

    # @api.depends('partner_id')
    # def _get_vendor_code(self):
    #     for rec in self:
    #         if rec.partner_id:
    #             rec.vendor_code = rec.partner_id.vendor
    #         else:
    #             rec.vendor_code = False




    # change the string Date Planned to Due Date
    date_planned = fields.Datetime(
        string='Due date', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")




    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()

        return self.action_view_invoice(moves)




    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
            result['context'] = [{'default_transaction_type': 'vendor_bill'}]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        invoices.write({
        'transaction_type': 'vendor_bill'})
        return result







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
        self.vendor_code = onc_vend.vendor


    def _bak_order(self):
        '''
        This function check the back order,if any back order show in BkOrds field.
        '''
        for r in self:
            bk_orders = self.env['stock.picking'].search([('origin', '=', r.name), ('company_id', '=', r.company_id.id),('state', '!=', 'done')],limit=1)
      
            if bk_orders:

                # for r in bk_orders:

                if bk_orders.backorder_id and bk_orders.state != 'done':

                    r.BkOrds = 'Y'
                else:
                    r.BkOrds = 'N'
            else:
                r.BkOrds = 'N'


        # if bk_orders:

        #     if bk_orders.backorder_id and bk_orders.state != 'done':
        #
        #         self.BkOrds = 'Y'
        #     else:
        #         self.BkOrds = 'N'
        # else:
        #     self.BkOrds = 'N'






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
    OM = fields.Float()
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
    desc_sku = fields.Char(related='product_id.product_tmpl_id.sku', string='Description', readonly=False)
    primary_locations = fields.Many2one('stock.location',string="Primary Location", related='product_id.product_tmpl_id.primary_location')


    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, context='show_desc'):
    #     args = list(args or [])
    #     if name:
    #         args += ['|', ('desc_sku', operator, name), ('product.id', operator, name)]
    #     return self._search(args, limit=limit, access_rights_uid=name_get_uid)
    #     return args.name_get()
    #
    #
    # def name_get(self):
    #     result=[]
    #     for rec in self:
    #         if self.env.context.get('show_desc', False):
    #             if rec.vendor:
    #                 sku_id = rec.product_id
    #                 desc = rec.desc_sku
    #                 sku_id_desc = str(rec.product_id) + '-' + str(rec. desc_sku)
    #             result.append((rec.id, sku_id_desc))


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
    _inherit = 'account.move.line'

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.move_id.move_type == 'in_invoice' or self.move_id.move_type == 'in_refund':
            actual_qty = 0
            rec_qty = 0
            if self.product_id:
                if self.purchase_order_id:
                    purchase_lines = self.env['purchase.order.line'].search([('product_id','=',self.product_id.id),('order_id','=', self.purchase_order_id.name)])
                    for i in purchase_lines:
                        actual_qty += i.product_qty
                        rec_qty += i.qty_received
                    if self.quantity > rec_qty or self.quantity < rec_qty:
                        res = {'warning': {'title': _('Warning'),'message': _('Vendor Bill and PO do not match - quantities not matching.')}}
                        return res

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        if self.move_id.move_type == 'in_invoice' or self.move_id.move_type == 'in_refund':
            if self.product_id:
                if self.price_unit:
                    purchase_lines = self.env['purchase.order.line'].search([('product_id','=',self.product_id.id),('order_id','=', self.purchase_order_id.name)])
                if self.price_unit:
                    if self.price_unit != purchase_lines.price_unit:
                        res = {'warning': {'title': _('Warning'),'message': _('Vendor Bill and PO do not match - Prices not matching.')}}
                        return res









