from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Inventory department validation

class myInventoryDepartment(models.Model):
    _inherit = 'hr.department'


    @api.model
    def create(self, values):
        if 'name' in values:
            same_name = self.env['hr.department'].search([('name', '=', values['name'])])
            if same_name:
                raise ValidationError('This department is already available')
            else:
                department = super(myInventoryDepartment, self).create(values)
        return department