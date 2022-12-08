from odoo import fields, models,api
from odoo.exceptions import ValidationError
import json
import logging

class PosConnect2Configuration(models.Model):
    _name = "pos_connect2.configuration"


    name = fields.Char(string="Name", help="Name of this Connect2 configuration")
    terminal_number = fields.Char(string="Terminal NUmber")
    merchant_number = fields.Char(string="Merchant Number")
    credit_plan_number = fields.Char(string="Credit Plan Number")
    descriptive_billing_code = fields.Char(string="Descriptive Billing Code(s) (DBC)")
    john_deere_financial_legal_invoice_disclosure = fields.Char(string="John Deere - Financial Legal Invoice Disclosure")
    dbc_code =fields.Many2one('pos.dbc.code', string="DBC")
    api_url = fields.Char(string="URL")

    active_record =fields.Boolean(string="Active",default=True)

    def toggle_active_record(self):
        if self.active_record:
            self.active_record = False
        else:
            self.active_record = True

class partner(models.Model):
    _inherit = "res.partner"

    card_number = fields.Char(string="John Deere Card Number")

class pos_connect2_transaction(models.Model):
    _name = "pos.connect.transaction"

    name =fields.Char(string="Order Number")
    invoice_no = fields.Char(string="Invoice Number")
    tr_status = fields.Char(string="Transaction Status")
    payment_type = fields.Char(string="")
    inv_amount = fields.Char(string="Invoice Amount")
    customer = fields.Many2one('res.partner')
    card_number = fields.Char(string="Card")
    dbc_code = fields.Char(string="DBC")
    credit_plan_number = fields.Char(string="Credit Plan Number")
    authorization_no = fields.Char(string="Auth. No")
    reference_no = fields.Char(string="Ref. No")


    @api.model
    def create(self, vals):
       if vals.get('name', 'New') == 'New':
           vals['name'] = self.env['ir.sequence'].next_by_code(
               'pos.connect.transaction') or 'New'
       result = super(pos_connect2_transaction, self).create(vals)
       return result

class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.model
    # def wk_register_invoice_payment(self, kwargs):
    #
    #     print ("inside==================== pos  invoice")
    #     if(kwargs.get('invoice_id')):
    #         invoice = self.browse(kwargs.get('invoice_id'))
    #
    #         journal_id = self.env['account.journal'].search(
    #             [('id', '=', kwargs.get('journal_id'))])
    #         available_payment_methods = journal_id.inbound_payment_method_line_ids
    #         payment_method_line_id = False
    #         if available_payment_methods:
    #             payment_method_line_id = available_payment_methods[0].id
    #
    #         payment_vals = {
    #             'amount': kwargs.get('amount'),
    #             'payment_type': 'inbound',
    #             'partner_type': 'customer',
    #             'ref': kwargs.get('payment_memo') or '',
    #             'journal_id': kwargs.get('journal_id'),
    #             'currency_id': invoice.currency_id.id,
    #             'partner_id': invoice.partner_id.id,
    #             'partner_bank_id': False,
    #             'payment_method_line_id': payment_method_line_id,
    #             'write_off_line_vals': {}
    #         }
    #         payment_id = self.env['account.payment'].create([payment_vals])
    #
    #         if payment_id:
    #             payment_id.action_post()
    #             line_id = False
    #             for line in payment_id.line_ids:
    #                 if line.account_internal_type in ['payable', 'receivable']:
    #                     line_id = line.id
    #             if line_id:
    #                 self.wk_assign_outstanding_credit_current(
    #                     invoice.id, line_id)
    #
    #         return {
    #             'residual': invoice.amount_residual,
    #             'state': invoice.state
    #         }

class posDBCcode(models.Model):
    _name = "pos.dbc.code"


    name = fields.Char(string="Code")
    description = fields.Char(string="Description")
    catagory = fields.Char(string="Category")

    @api.model
    def add_dbc_code(self,args,**kwargs):
        return [i.name for i in self.search([])]

class posOrder(models.Model):
    _inherit = "pos.order"

    legal_disclosure =fields.Char(string="Legal Disclosure")
    



