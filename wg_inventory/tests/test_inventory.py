# from odoo.addons.sale.tests.common import TestSaleCommon
# from odoo.exceptions import AccessError, UserError, ValidationError
# from odoo.tests import HttpCase, tagged


# @tagged('post_install', '-at_install')
# class TestAccessRights(TestSaleCommon):


	# ./odoo-bin -i wg_inventory --test-tags nice --addons-path=/opt/odoo14/odoo/addons/




from odoo.tests.common import TransactionCase, tagged, SavepointCase,Form 
 
@tagged('-standard', 'nice') 
class TestInventory(TransactionCase):
 
    def setUp(self):
        super(TestInventory, self).setUp()
