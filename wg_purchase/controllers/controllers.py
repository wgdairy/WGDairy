# -*- coding: utf-8 -*-
# from odoo import http


# class WgPurchase(http.Controller):
#     @http.route('/wg_purchase/wg_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wg_purchase/wg_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wg_purchase.listing', {
#             'root': '/wg_purchase/wg_purchase',
#             'objects': http.request.env['wg_purchase.wg_purchase'].search([]),
#         })

#     @http.route('/wg_purchase/wg_purchase/objects/<model("wg_purchase.wg_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wg_purchase.object', {
#             'object': obj
#         })
