# -*- coding: utf-8 -*-
from odoo import http


class WgdCustomer(http.Controller):
    @http.route('/wgd_customer/wgd_customer', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/wgd_customer/wgd_customer/objects', auth='public')
    def list(self, **kw):
        return http.request.render('wgd_customer.listing', {
            'root': '/wgd_customer/wgd_customer',
            'objects': http.request.env['wgd_customer.wgd_customer'].search([]),
        })

    @http.route('/wgd_customer/wgd_customer/objects/<model("wgd_customer.wgd_customer"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('wgd_customer.object', {
            'object': obj
        })
