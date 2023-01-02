# -*- coding: utf-8 -*-
{
    'name': "wg_inventory",

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
    'depends': ['base', 'stock', 'product', 'account', 'vendors'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/inventory_main.xml',
        'views/receiving_po_new.xml',
        'views/warehouse_store_menu.xml',
        # 'reports/Receiving_Products.xml',
        'reports/inventory_transfer.xml',
        'views/recrules.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/wg_inventory/static/src/style.css',
            'wg_inventory/static/src/js/pos_product_view.js',
        ],
        'web.assets_qweb': [
            'wg_inventory/static/src/xml/**/*'
        ],
}

}
