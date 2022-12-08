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
from odoo.http import request,Response
from odoo import http
import logging
import json
_logger = logging.getLogger(__name__)



class ConnectPayment(http.Controller):


    def __init__(self):
        self.current_screen = None



    @http.route('/pos/payment/<int:id>/update', type='json', auth='none')
    def update_payment_screen(self,**kw):
        _logger.info("********************kw dta****************:%r",kw)
        screen_config = request.env['pos.payment.screen.config'].sudo().browse(kw.get('id'))
        data_to_send = {}
        _logger.info("***********self.current******:%r",self.current_screen)
        if kw.get('is_refresh'):
            _logger.info("**********run inside**************")
            screen_config.is_update = True
        if(screen_config.is_update and screen_config.related_id.type_of_payment_screen == 'screen'):
            screen_type = screen_config.type_of_screen
            pos_name = screen_config.related_id and screen_config.related_id.name
            company = screen_config.related_id and screen_config.related_id.company_id.name
            # return screen_type
            if screen_type != kw.get('template_screen_type'):
                if screen_type == 'welcome':
                    self.current_screen = 'welcome'
                    screen_data = screen_config.read([])
                    images = request.env['promotion.image'].sudo().browse(screen_data[0].get('promotions_pictures')).read(['image'])
                    _logger.info("*************images**********:%r",images)
                    _logger.info("*************screen_data**********:%r",screen_data)
                    data_to_send.update({
                        'screen_data':screen_data,
                        'images':images,
                        'type_of_screen':screen_type,
                        'pos_name':pos_name,
                        'company':company
                    })
                else:
                    self.current_screen = 'payment'
                    new_paymentline = request.env['pos.payment.transaction'].sudo().search([('state','=','draft'),('created_from','=','screen')],limit=1,order="id desc")
                    payment_amount = new_paymentline.amount_with_currency
                    data_to_send.update({
                        'type_of_screen':screen_type,
                        'payment_data':new_paymentline.read([]),
                        'pos_name':pos_name,
                        'company':company,
                        'payment_amount':payment_amount,
                        # 'customer_name':
                    })
                    if new_paymentline.partner_id:
                        data_to_send.update({'customer_name':new_paymentline.partner_id.name})

                    
        return data_to_send


    @http.route('/pos/payment/<int:id>/screen', type='http', auth='none')
    def render_pos_payment_screen(self):
        return request.render('pos_connect2_payment_acquirer.pos_payment_screen_template')



