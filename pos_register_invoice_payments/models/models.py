# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def wk_register_invoice_payment(self, kwargs):

        print("-----------=-6347637737==============")
        if(kwargs.get('invoice_id')):
            invoice = self.browse(kwargs.get('invoice_id'))

            journal_id = self.env['account.journal'].search(
                [('id', '=', kwargs.get('journal_id'))])
            available_payment_methods = journal_id.inbound_payment_method_line_ids
            payment_method_line_id = False
            if available_payment_methods:
                payment_method_line_id = available_payment_methods[0].id

            payment_vals = {
                'amount': kwargs.get('amount'),
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'ref': kwargs.get('payment_memo') or '',
                'journal_id': kwargs.get('journal_id'),
                'currency_id': invoice.currency_id.id,
                'partner_id': invoice.partner_id.id,
                'partner_bank_id': False,
                'payment_method_line_id': payment_method_line_id,
                'write_off_line_vals': {}
            }
            print ("valsssssss=======",payment_vals)
            payment_id = self.env['account.payment'].create([payment_vals])
            print("=====dwdwdw===",payment_id)

            if payment_id:
                payment_id.action_post()
                line_id = False
                for line in payment_id.line_ids:
                    if line.account_internal_type in ['payable', 'receivable']:
                        line_id = line.id
                if line_id:
                    self.wk_assign_outstanding_credit_current(
                        invoice.id, line_id)

            return {
                'residual': invoice.amount_residual,
                'state': invoice.state
            }

    def wk_assign_outstanding_credit_current(self, invoice_id, line_id):
        invoice = self.env['account.move'].search([('id', '=', invoice_id)])
        if invoice:
            lines = self.env['account.move.line'].browse(line_id)
            lines += invoice.line_ids.filtered(
                lambda line: line.account_id == lines[0].account_id and not line.reconciled)
            wk_register = lines.reconcile()
            if(wk_register):
                return invoice.read(['invoice_outstanding_credits_debits_widget', 'invoice_payments_widget', 'state', 'amount_total', 'amount_residual'])
            else:
                return False

    def wk_assign_outstanding_credit(self, line_id):
        self.ensure_one()
        lines = self.env['account.move.line'].browse(line_id)
        lines += self.line_ids.filtered(lambda line: line.account_id ==
                                        lines[0].account_id and not line.reconciled)
        wk_register = lines.reconcile()
        if(wk_register):
            return self.read(['invoice_outstanding_credits_debits_widget', 'invoice_payments_widget', 'state', 'amount_total', 'amount_residual'])
        else:
            return False

    @api.model
    def enable_accounting_group(self):
        try:
            self.env.ref('account.group_account_user').write(
                {'users': [(4, self.env.ref('base.user_admin').id)]})
        except Exception as e:
            _logger.info("*****************Exception**************", e)


class AccountJournals(models.Model):
    _inherit = "account.journal"


    john_deere_payment_method = fields.Boolean(String= "Allow payment using John Deere")

    @api.model
    def get_journal(self, args):

        return self.browse(args['journal']).john_deere_payment_method 
