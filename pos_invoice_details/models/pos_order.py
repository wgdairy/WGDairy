# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self,orders, draft=False):
        order_ids = super(PosOrder,self).create_from_ui(orders,draft)    
        for order_id in order_ids:
            order_id['invoices'] = []
            order_id['invoice_lines'] = []
            if(order_id.get('id')):
                order = self.browse([order_id.get('id')])
                if order.account_move:
                    invoice_vals = {}
                    invoice_vals['id'] = order.account_move.id
                    invoice_vals['name'] = order.account_move.name
                    invoice_vals['partner_id'] = [order.account_move.partner_id.id, order.account_move.partner_id.name]
                    invoice_vals['invoice_date'] = order.account_move.invoice_date
                    invoice_vals['amount_total'] = order.account_move.amount_total
                    invoice_vals['amount_residual'] = order.account_move.amount_residual
                    invoice_vals['invoice_user_id'] = [order.account_move.invoice_user_id.id, order.account_move.invoice_user_id.name]
                    invoice_vals['state'] = order.account_move.state
                    invoice_vals['invoice_line_ids'] = []
                    for invoice_line in order.account_move.invoice_line_ids:
                        invoice_line_vals = {}
                        invoice_vals['invoice_line_ids'].append(invoice_line.id)
                        invoice_line_vals['id'] = invoice_line.id
                        invoice_line_vals['product_id'] = [invoice_line.product_id.id, invoice_line.product_id.name]
                        invoice_line_vals['name'] = invoice_line.name
                        invoice_line_vals['account_id'] = [invoice_line.account_id.id, invoice_line.account_id.name]
                        invoice_line_vals['quantity'] = invoice_line.quantity
                        invoice_line_vals['price_unit'] = invoice_line.price_unit
                        invoice_line_vals['price_subtotal'] = invoice_line.price_subtotal
                        invoice_line_vals['tax_ids'] = []
                        for invoice_line_tax in invoice_line.tax_ids:
                            invoice_line_vals['tax_ids'].append(invoice_line_tax.id)                
                        order_id['invoice_lines'].append(invoice_line_vals)
                    order_id['invoices'].append(invoice_vals)
        return order_ids
