# -*- coding: utf-8 -*-
# from odoo import http


# class WgdFieldService(http.Controller):
#     @http.route('/wgd_field_service/wgd_field_service', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wgd_field_service/wgd_field_service/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wgd_field_service.listing', {
#             'root': '/wgd_field_service/wgd_field_service',
#             'objects': http.request.env['wgd_field_service.wgd_field_service'].search([]),
#         })

#     @http.route('/wgd_field_service/wgd_field_service/objects/<model("wgd_field_service.wgd_field_service"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wgd_field_service.object', {
#             'object': obj
#         })
