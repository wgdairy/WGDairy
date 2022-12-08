# -*- coding: utf-8 -*-
# from odoo import http


# class WgInventory(http.Controller):
#     @http.route('/wg_inventory/wg_inventory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wg_inventory/wg_inventory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wg_inventory.listing', {
#             'root': '/wg_inventory/wg_inventory',
#             'objects': http.request.env['wg_inventory.wg_inventory'].search([]),
#         })

#     @http.route('/wg_inventory/wg_inventory/objects/<model("wg_inventory.wg_inventory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wg_inventory.object', {
#             'object': obj
#         })
