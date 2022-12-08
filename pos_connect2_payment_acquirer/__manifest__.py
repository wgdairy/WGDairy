# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "John Deere Payment Acquirer",
  "summary"              :  """It provides a handy payment method through which the customer can do their payments via John Deere.""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0",
  "author"               :  "Ontash India Technologies.",
  "license"              :  "Other proprietary",
  "website"              :  "https://www.ontash.net",
  "description"          :  """""",
  "live_test_url"        :  "",
  "depends"              :  ['point_of_sale',],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/pos_connect2_view.xml',
                             'views/pos_payment_screen_views.xml',
                             'views/pos_connect2_config.xml',
                            # 'views/templates.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
 # "qweb"                 :  ['static/src/xml/pos_connect.xml'],
  "assets"               : {

                    		'point_of_sale.assets':
                    				 ['pos_connect2_payment_acquirer/static/src/js/main.js',
                    			      'pos_connect2_payment_acquirer/static/src/js/PaymentNotifyPopupWidget.js',
                                      'pos_connect2_payment_acquirer/static/src/js/PaymentScreen.js',
                                      'pos_connect2_payment_acquirer/static/src/js/PaymentScreenPaymentLines.js',
                                      'pos_connect2_payment_acquirer/static/src/js/ConnectPaymentPopUp.js',
                                      'pos_connect2_payment_acquirer/static/src/js/Pos_register_invoice_payments_inherit.js',
                                      'pos_connect2_payment_acquirer/static/src/css/main.css',


                    				],
                    			'web.assets_qweb': [
                    				    'pos_connect2_payment_acquirer/static/src/xml/**/*',
                                # 'pos_connect2_payment_acquirer/static/src/xml/pos_receipt_inherit.xml',
                    				],
                                'pos_connect2_payment_acquirer.display_assets':[
                                    'pos_connect2_payment_acquirer/static/lib/js/payment_screen.js',
                                    'pos_connect2_payment_acquirer/static/lib/css/payment_screen.css'
                            ],

                    						    },
  "images"               :  ['static/description/Banner.png'],
  "active"               :  False,
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  79,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
