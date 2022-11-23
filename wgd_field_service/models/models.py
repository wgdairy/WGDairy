# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class wgd_field_service(models.Model):
#     _name = 'wgd_field_service.wgd_field_service'
#     _description = 'wgd_field_service.wgd_field_service'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


#access_wgd_field_service_wgd_field_service,wgd_field_service.wgd_field_service,model_wgd_field_service_wgd_field_service,base.group_user,1,1,1,1

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict
from odoo.tools.misc import format_date

class TripsTolls(models.Model):
    _name = 'trips.tolls'
    _description = 'Trips and Tolls'
    
    @api.model
    def get_mileage(self):
        mileage = self.env['product.template'].search([('name', '=ilike', 'mileage')], limit=1)
        return mileage
    sku = fields.Many2one('product.template', default=get_mileage)
    date = fields.Date()
    trips_tolls = fields.Selection([('trips','Trips'),('tolls', 'Tolls')])
    qty = fields.Integer()
    description = fields.Text()
    unit_price = fields.Float()
    ext_price = fields.Float(compute="_compute_ext_price")
    task = fields.Many2one('project.task')

    @api.depends('qty', 'unit_price')
    def _compute_ext_price(self):
        for record in self:
            record.ext_price = record.qty * record.unit_price

    @api.onchange('qty')
    def validate_qty(self):
        if self.qty:
            if len(str(self.qty)) > 7:
                raise ValidationError("5 digits be allowed in qty")

    @api.onchange('unit_price')
    def validate_Unit_Price(self):
        if self.unit_price:
            if len(str(self.unit_price)) > 12:
                raise ValidationError("10 digits be allowed in Unit_Price")

    @api.onchange('unit_amount')
    def validate_hours_spent(self):
        for record in self:
            if record.unit_amount not in range(0,25):
                raise ValidationError("Please enter valid hours")

class InheritTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    unit_price      = fields.Float()
    ext_price       = fields.Float(compute="_compute_ext_price")
    total_price     = fields.Float()
   # timesheet_ids = fields.Many2one('project.task')
            
    @api.depends('unit_amount', 'unit_price')
    def _compute_ext_price(self):
        for record in self:
            record.ext_price = record.unit_amount * record.unit_price

    def validate_float(self, float_value, val):
        if float_value:
            if len(str(float_value)) > 12:
                raise ValidationError("10 digits be allowed in %s" % val)

    @api.constrains('unit_price')
    def float_limit(self):
        if self.unit_price:
            val = "Unit Price"
            self.validate_float(self.unit_price,val)
            
class InheritTask(models.Model):
    _inherit = 'project.task'

    trips_tolls = fields.One2many('trips.tolls', 'task')
    product_id = fields.Many2one('product.template', domain=[('name','ilike','Labor')])

    def action_fsm_validate(self):
        """ If allow billable on task, timesheet product set on project and user has privileges :
            Create SO confirmed with time and material.
        """
        super().action_fsm_validate()
        billable_tasks = self.filtered(lambda task: task.allow_billable and (task.allow_timesheets or task.allow_material))
        timesheets_read_group = self.env['account.analytic.line'].sudo().read_group([('task_id', 'in', billable_tasks.ids), ('project_id', '!=', False)], ['task_id', 'id'], ['task_id'])
        timesheet_count_by_task_dict = {timesheet['task_id'][0]: timesheet['task_id_count'] for timesheet in timesheets_read_group}
        for task in billable_tasks:
            timesheet_count = timesheet_count_by_task_dict.get(task.id)
            if not task.sale_order_id and not timesheet_count:  # Prevent creating/confirming a SO if there are no products and timesheets
                continue
            task._fsm_ensure_sale_order()
            task._fsm_create_sale_order_line()
            task._append_trips_tolls()
            task._append_stock_misc()
            if task.sudo().sale_order_id.state in ['draft', 'sent']:
                task.sudo().sale_order_id.action_confirm()
        billable_tasks._prepare_materials_delivery()

    def _append_trips_tolls(self):
        self.ensure_one()
        if self.sale_order_id:
            for rec in self.trips_tolls:
                print(rec.qty, rec.unit_price, rec.qty, rec.sku.uom_id, rec.sku.id)
                self.env['sale.order.line'].create({
                    'order_id': self.sale_order_id.id,
                    'product_id': rec.sku.product_variant_id.id,
                    # The project and the task are given to prevent the SOL to create a new project or task based on the config of the product.
                    'project_id': self.project_id.id,
                    'task_id': self.id,
                    'product_uom_qty': rec.qty,
                    'product_uom': rec.sku.uom_id.id,
                    'price_unit': rec.unit_price,
                })

    def _append_stock_misc(self):
        self.ensure_one()
        if self.sale_order_id:
            for rec in self.stock_mic_ids:
                self.env['sale.order.line'].sudo().create({
                    'order_id': self.sale_order_id.id,
                    'product_id': rec.sku_id.product_variant_id.id,
                    # The project and the task are given to prevent the SOL to create a new project or task based on the config of the product.
                    'project_id': self.project_id.id,
                    'task_id': self.id,
                    'product_uom_qty': rec.qty,
                    'product_uom': rec.sku_id.uom_id.id,
                    'price_unit': rec.Unit_Price,
                })

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def _get_customer(self):
    #     if self.partner_id:
    #         print(self.partner_id)
    #     customer = self.env['my.customer'].search([('partner_id','=','demo')], limit=1)
    #     print(customer,'afs---------------')
    #     return 'customer'
    
    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            if self.partner_id.taxable == "yes":
                taxes = self.env['account.tax'].search([('company_id','=',self.company_id.id),('type_tax_use','=','sale')], limit=1)
                self.w_tax = taxes
            else:
                self.w_tax = False
            # customer = self.env['my.customer'].search([('partner_id','=',self.partner_id.id)], limit=1)
            # self.job_no = customer.job_ids
            # self.payment_term_id = customer.terms_code
            self.job_ord_no = self.partner_id.job_ids

    @api.onchange('company_id')
    def onchange_company(self):
        if self.company_id and self.partner_id:
            taxes = self.env['account.tax'].search([('company_id','=',self.company_id.id),('type_tax_use','=','sale')], limit=1)
            self.w_tax = taxes

    job_ord_no = fields.Many2one('wgd.job.no',default=lambda self: self.env['wgd.job.no'].search([('name','=','0')]), limit=1)
    po_no = fields.Integer()
    clerk = fields.Many2one('res.users', default=lambda self:self.env.user)
    terminal = fields.Char()
    w_date = fields.Datetime()
    w_order = fields.Integer()
    del_date = fields.Date()
    w_tax = fields.Many2one('account.tax')
    ship_to = fields.Char('Address')
    ship_to_street = fields.Char('Street')
    ship_to_city = fields.Char('City')
    ship_to_state = fields.Many2one('res.country.state', string='State', ondelete='restrict')
    ship_to_country = fields.Many2one('res.country', string='Country', ondelete='restrict')
    zip_code = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", default=lambda self: self.partner_id.property_payment_term_id)

    
    

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    avg_cost = fields.Monetary(string="Average Cost")
    description = fields.Char('Description', related='product_id.name', readonly=False)
    # tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)], default=lambda self:self.order_id.w_tax)

    @api.onchange('product_id')
    def onchange_tax(self):
        if self.product_id:
            self.avg_cost = self.product_id.avg_cost_pricing
    # @api.onchange('product_id')
    # def onchange_tax(self):
    #     print(self.order_id.w_tax)
    #     if self.order_id.w_tax:
    #         self.tax_id = self.order_id.w_tax


class CustomerInvoiceInherit(models.Model):
    _inherit = 'account.move'

    job_ord_no = fields.Many2one('wgd.job.no', default=lambda self: self.env['wgd.job.no'].search([('name','=','0')]), limit=1)
    clerk = fields.Many2one('res.users', default=lambda self:self.env.user)
    w_tax = fields.Many2one('account.tax',default=lambda self: self.env['account.tax'].search([('company_id','=',self.company_id.id)]), limit=1)
    ship_to = fields.Char('Address')
    ship_to_street = fields.Char('Street')
    ship_to_city = fields.Char('City')
    ship_to_state = fields.Many2one('res.country.state', string='State', ondelete='restrict')
    ship_to_country = fields.Many2one('res.country', string='Country', ondelete='restrict')
    zip_code = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", default=lambda self: self.partner_id.property_payment_term_id)

    
    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            if self.partner_id.taxable == "yes":
                taxes = self.env['account.tax'].search([('company_id','=',self.company_id.id),('type_tax_use','=','sale')], limit=1)
                self.w_tax = taxes
            else:
                self.w_tax = False
            customer = self.env['my.customer'].search([('partner_id','=',self.partner_id.id)], limit=1)
            self.job_ord_no = customer.job_ids
            self.payment_term_id = customer.terms_code

    @api.onchange('company_id')
    def onchange_company(self):
        if self.company_id and self.partner_id:
            taxes = self.env['account.tax'].search([('company_id','=',self.company_id.id)], limit=1)
            self.w_tax = taxes

class SaleOrderFieldServiceInherit(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        """
        TO override the the method to transfer value from SO to invoice.
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))
        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'payment_term_id': self.payment_term_id.id,
            'job_ord_no':self.job_ord_no.id,
            'clerk':self.clerk.id,
            'w_tax':self.w_tax.id,
            'ship_to':self.ship_to,
            'ship_to_street':self.ship_to_street,
            'ship_to_city':self.ship_to_city,
            'ship_to_state':self.ship_to_state.id,
            'ship_to_country':self.ship_to_country.id,
            'zip_code':self.zip_code,
            'country_id':self.country_id.id,
        }
        return invoice_vals

class AccountingReportInherit(models.AbstractModel):
    _inherit = 'account.aged.partner'

    @api.model
    def _get_column_details(self, options):
        columns = [
            self._header_column(),
            self._field_column('report_date'),

            self._field_column('account_name', name=_("Account"), ellipsis=True),
            self._field_column('expected_pay_date'),
            self._field_column('period0', name=_("Current")),
            self._field_column('period1', sortable=True),
            self._field_column('period2', sortable=True),
            self._field_column('period3', sortable=True),
            self._field_column('period4',name=_("90+"), sortable=True),
            self._field_column('period5', sortable=True),
            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_('Total'),
                classes=['number'],
                formatter=self.format_value,
                getter=(lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v['period5']),
                sortable=True,
            ),
        ]

        if self.user_has_groups('base.group_multi_currency'):
            columns[2:2] = [
                self._field_column('amount_currency'),
                self._field_column('currency_id'),
            ]
        return columns

    def _format_partner_id_line(self, res, value_dict, options):
        res['name'] = value_dict['partner_name'][:128] if value_dict['partner_name'] else _('Unknown Partner')
        res['trust'] = value_dict['partner_trust']
        partner = self.env['res.partner'].browse(res['partner_id'])
        res['customer_id'] = partner.customer_id


class PartnerLedgerReport(models.AbstractModel):
    _inherit = "account.partner.ledger"

    @api.model
    def _get_report_line_total(self, options, initial_balance, debit, credit, balance):
        columns = [
            # {'name': self.format_value(initial_balance), 'class': 'number'},
            {'name': self.format_value(debit), 'class': 'number'},
            {'name': self.format_value(credit), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': ''})
        columns.append({'name': self.format_value(balance), 'class': 'number'})
        return {
            'id': 'partner_ledger_total_%s' % self.env.company.id,
            'name': _('Total'),
            'class': 'total',
            'level': 1,
            'columns': columns,
            'colspan': 6,
        }

    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        if aml['payment_id']:
            caret_type = 'account.payment'
        else:
            caret_type = 'account.move'

        date_maturity = aml['date_maturity'] and format_date(self.env, fields.Date.from_string(aml['date_maturity']))
        columns = [
            {'name': aml['journal_code']},
            {'name': aml['account_code']},
            {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'class': 'o_account_report_line_ellipsis'},
            {'name': date_maturity or '', 'class': 'date'},
            {'name': aml['matching_number'] or ''},
            # {'name': self.format_value(cumulated_init_balance), 'class': 'number'},
            {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
            {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            if aml['currency_id']:
                currency = self.env['res.currency'].browse(aml['currency_id'])
                formatted_amount = self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True)
                columns.append({'name': formatted_amount, 'class': 'number'})
            else:
                columns.append({'name': ''})
        columns.append({'name': self.format_value(cumulated_balance), 'class': 'number'})
        return {
            'id': aml['id'],
            'parent_id': 'partner_%s' % (partner.id if partner else 0),
            'name': format_date(self.env, aml['date']),
            'class': 'text' + aml.get('class', ''),  # do not format as date to prevent text centering
            'columns': columns,
            'caret_options': caret_type,
            'level': 2,
        }

    @api.model
    def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
        company_currency = self.env.company.currency_id
        unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')

        columns = [
            # {'name': self.format_value(initial_balance), 'class': 'number'},
            {'name': '', 'class': 'number'},
            {'name': '', 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': ''})
        columns.append({'name': self.format_value(initial_balance), 'class': 'number'})

        return {
            'id': 'partner_%s' % (partner.id if partner else 0),
            'partner_id': partner.id if partner else None,
            'name': partner is not None and (partner.name or '')[:128] or _('Unknown Partner'),
            'columns': columns,
            'level': 2,
            'trust': partner.trust if partner else None,
            'unfoldable': not company_currency.is_zero(debit) or not company_currency.is_zero(credit),
            'unfolded': 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines'] or unfold_all,
            'colspan': 6,
        }

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _('JRNL')},
            {'name': _('Account')},
            {'name': _('Ref')},
            {'name': _('Due Date'), 'class': 'date'},
            {'name': _('Matching Number')},
            {'name': _('Initial Balance'), 'class': 'number','pl_report':True},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'}]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns