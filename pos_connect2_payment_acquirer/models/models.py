# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, models,api
from odoo.exceptions import ValidationError
import json
import logging
_logger = logging.getLogger(__name__)




class AccountJournal(models.Model):
    _inherit = "pos.payment.method"

    connect_payment_method = fields.Boolean("Allow Payments Via John Deere")


    @api.model
    def create_connect_payment_method(self):
        pos_config = self.env['pos.config'].search([])
        journal = self.env['pos.payment.method']
        if pos_config:
            pos_config = pos_config[0]
            ctx = dict(self.env.context, company_id=pos_config.company_id.id)
            connect_payment_method = journal.with_context(ctx).search([('name','=','Connect'),('is_cash_count', '=', False)])
            if connect_payment_method:
                connect_payment_method.write({'connect_payment_method':True})
            else:
                connect_payment_method = journal.with_context(ctx).create({'name':'Connect','is_cash_count':False,'connect_payment_method':True})
                if not connect_payment_method.id in pos_config.payment_method_ids.ids:
                    pos_config.sudo().write({'payment_method_ids':[(4,connect_payment_method.id)]})



class PosWeChatConfiguration(models.Model):
    _name = "pos_connect.configuration"

    name = fields.Char(string="Name", help="Name of this Connect configuration")
    publishable_key = fields.Text(string="Publishable API Key",required=True, help="Api Key of user to autheticate him on the payment service provider.")
    secret_key = fields.Text(string="Secret API Key",required=True, help="Api Key of user to autheticate him on the payment service provider.")
    active_record = fields.Boolean(default=False,readonly=True)

    @api.constrains('active_record')
    def validate_single_api_key(self):
        records = self.search([])
        count = 0
        for record in records:
            if record.active_record == True:
                count += 1
        if(count >1):
            raise ValidationError("You can't have two active credentials.")



    def toggle_active_record(self):
        if self.active_record:
            self.active_record = False
        else:
            self.active_record = True

class PosOrder(models.Model):
    _inherit = "pos.order"

    def _payment_fields(self,  order, ui_paymentline):
        result = super(PosOrder, self)._payment_fields( order, ui_paymentline)
        if ui_paymentline.get('src_id'):
            result.update({
                'connect_src_id':ui_paymentline.get('src_id')
            })
        return result

class AccountBankStatementLine(models.Model):
    _inherit = 'pos.payment'

    connect_src_id = fields.Text(string="Connect Source ID")

class PosPaymentTransaction(models.Model):
    _name = 'pos.payment.transaction'

    payment_amount = fields.Float(string="Payment Amount")
    order_ref = fields.Char(string="Order Ref")
    txn_id = fields.Text(string="Transaction ID")
    state = fields.Selection([('draft','New'),('pending','Pending'),('failed','Failed'),('done','Done')],string="State")
    created_from = fields.Selection([('pos','POS'),('screen','Screen')],string="Created From")
    txn_data = fields.Text(string="Transaction Data")
    fail_reason = fields.Text(string="Reason of Failure")
    amount_with_currency = fields.Char(string="Payment Amount")
    name_on_card = fields.Char(string="Name On Card")
    mobile_no = fields.Char(string="Mobile No.")
    partner_id = fields.Many2one('res.partner',string="Customer Name")


    @api.model
    def create_payment_transaction(self,data,order_ref,amount,screen_id,config_id,created_from,amount_with_currency,partner_id,state):
        transaction_data = json.loads(data)
        screen_id = self.env['pos.payment.screen.config'].browse(screen_id)
        if screen_id:
            screen_id.is_update = True
            screen_id.type_of_screen ='payment'
        vals = {
            'txn_id':transaction_data.get('txn_id'),
            'payment_amount':amount,
            'state':state,
            'order_ref':order_ref,
            'txn_data':data,
            'created_from':created_from,
            'amount_with_currency':amount_with_currency,
            'partner_id':partner_id
        }
        res = self.create(vals)
        screen_config = self.env['pos.payment.screen.config'].browse(config_id)
        screen_config.write({
            'type_of_screen':'payment',
            'is_update':True
        })
        return res.id

    @api.model
    def update_payment_status(self,is_update,status,pos_txn_id,screen_config_id,customer_data):
        _logger.info("**********{}********{}*****".format(is_update,status))
        _logger.info("***********csutomer_data********:%r",customer_data)
        transaction = self.browse(pos_txn_id)
        vals = {}
        if is_update:
            if status ==  'succeeded':
                # transaction.state = 'done'
                vals.update({
                    'state':'done'
                })
        else:
            # transaction.state = 'failed'
            # transaction.fail_reason = status.get("message")
            vals.update({
                'state':'failed',
                'fail_reason':status.get('message')
            })
        if customer_data:
            vals.update({
                'name_on_card':customer_data.get('customer_name'),
                'mobile_no':customer_data.get('mobile_no')
            })
        transaction.write(vals)
        screen_config = self.env['pos.payment.screen.config'].browse(screen_config_id)
        config_vals = {
            'type_of_screen':'welcome',
            'is_update':True
        }
        screen_config.write(config_vals)
        
    @api.model
    def refresh_paymentline(self,pos_txn_id,screen_config_id):
        _logger.info("**********{}********{}*****".format(pos_txn_id,screen_config_id))
        transaction = self.browse(pos_txn_id)
        transaction.state = 'draft'
        screen_config = self.env['pos.payment.screen.config'].browse(screen_config_id)
        screen_config.write({
            'type_of_screen':'payment',
            'is_update':True
        })

    @api.model
    def cancel_popup_payment(self,pos_txn_id):
        transaction = self.browse(pos_txn_id)
        if transaction:
            transaction.write({'state':'failed','fail_reason':'Payment cancelled by user..'})
        