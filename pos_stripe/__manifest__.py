# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Stripe',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a Stripe payment terminal',
    'description': '',
    'data': [
        'views/res_config_settings_inherited1.xml',
        'views/pos_payment_method_views.xml',
        'views/assets_stripe.xml',
    ],
    'depends': ['base','point_of_sale', 'payment_stripe'],
    'installable': True,
    'assets': {
        'point_of_sale.assets': [
            'pos_stripe/static/**/*',
        ],
    },
    'license': 'LGPL-3',
}
