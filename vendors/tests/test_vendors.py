# from odoo.addons.sale.tests.common import TestSaleCommon
# from odoo.exceptions import AccessError, UserError, ValidationError
# from odoo.tests import HttpCase, tagged


# @tagged('post_install', '-at_install')
# class TestAccessRights(TestSaleCommon):


	# ./odoo-bin -i vendors --test-tags nice --addons-path=/usr/lib/python3/dist-packages/odoo/addons
	



from odoo.tests.common import TransactionCase, tagged, SavepointCase,Form 
 
@tagged('-standard', 'nice') 
class TestVendor(TransactionCase):
 
    def setUp(self):
        super(TestVendor, self).setUp()
