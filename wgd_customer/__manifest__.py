# -*- coding: utf-8 -*-
{
    'name': "wgd_customer",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/customer.xml',
        # 'views/views.xml',
        'views/templates.xml',
        'views/company.xml',
        'views/job_menu.xml',

    ],
    # css view
    'css': [
        'static/css/customer.css',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'wgd_customer/static/src/js/models.js',
        ],
        'web.assets_qweb': [
        'wgd_customer/static/src/xml/**/*'
        ],}
}
