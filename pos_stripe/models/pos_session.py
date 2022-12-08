# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.osv.expression import AND, OR
from odoo.service.common import exp_version


class PosStripeTest(models.TransientModel):
    _inherit = "res.config.settings"

    module_pos_stripe = fields.Boolean(string="Stripe Payment Terminal",
                                       help="The transactions are processed by Stripe. Set the IP address of the terminal on the related payment method.")


class PosSession(models.Model):
    _inherit = 'pos.session'

    # def _loader_params_pos_payment_method(self):
    #     result = super()._loader_params_pos_payment_method()
    #     result['search_params']['fields'].append('stripe_serial_number')
    #     print("\n\n\n\n\n*********************result new tto**++++++++++++++\n\n\n\n\n",result)
    #     return result

    # def _post_statement_difference(self, amount):
    #     if amount:
    #         if self.config_id.cash_control:
    #             st_line_vals = {
    #                 'journal_id': self.cash_journal_id.id,
    #                 'amount': amount,
    #                 'date': self.statement_line_ids.sorted()[-1:].date or fields.Date.context_today(self),
    #                 'pos_session_id': self.id,
    #             }
    #
    #     if self.cash_register_difference < 0.0:
    #         if not self.cash_journal_id.loss_account_id:
    #             raise UserError(
    #                 _('Please go on the %s journal and define a Loss Account. This account will be used to record cash difference.',
    #                   self.cash_journal_id.name))
    #
    #     st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Loss)")
    #     st_line_vals['counterpart_account_id'] = self.cash_journal_id.loss_account_id.id
    #     else:
    #     # self.cash_register_differe-nce > 0.0
    #     if not self.cash_journal_id.profit_account_id:
    #         raise UserError(
    #             _('Please go on the %s journal and define a Profit Account. This account will be used to record cash difference.',
    #               self.cash_journal_id.name))
    #
    #     st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Profit)")
    #     st_line_vals['counterpart_account_id'] = self.cash_journal_id.profit_account_id.id
    #
    #     self.env['account.bank.statement.line'].create(st_line_vals)

    def get_onboarding_data(self):
        return {
            "categories": self._load_model('pos.category'),
            "products": self._load_model('product.product'),
        }

    def _load_model(self, model):
        model_name = model.replace('.', '_')
        loader = getattr(self, '_get_pos_ui_%s' % model_name, None)
        params = getattr(self, '_loader_params_%s' % model_name, None)
        if loader and params:
            return loader(params())
        else:
            raise NotImplementedError(_("The function to load %s has not been implemented.", model))

    def load_pos_data(self):
        loaded_data = {}
        self = self.with_context(loaded_data=loaded_data)
        for model in self._pos_ui_models_to_load():
            loaded_data[model] = self._load_model(model)
        self._pos_data_process(loaded_data)
        return loaded_data

    def _get_attributes_by_ptal_id(self):
        product_attributes = self.env['product.attribute'].search([('create_variant', '=', 'no_variant')])
        product_attributes_by_id = {product_attribute.id: product_attribute for product_attribute in product_attributes}
        domain = [('attribute_id', 'in', product_attributes.mapped('id'))]
        product_template_attribute_values = self.env['product.template.attribute.value'].search(domain)
        key = lambda ptav: (ptav.attribute_line_id.id, ptav.attribute_id.id)
        res = {}
        for key, group in groupby(sorted(product_template_attribute_values, key=key), key=key):
            attribute_line_id, attribute_id = key
            values = [{**ptav.product_attribute_value_id.read(['name', 'is_custom', 'html_color'])[0],'price_extra': ptav.price_extra} for ptav in list(group)]
            res[attribute_line_id] = {
                'id': attribute_line_id,
                'name': product_attributes_by_id[attribute_id].name,
                'display_type': product_attributes_by_id[attribute_id].display_type,
                'values': values
            }

        return res

    def _pos_data_process(self, loaded_data):
        """
        This is where we need to process the data if we can't do it in the loader/getter
        """
        loaded_data['version'] = exp_version()

        loaded_data['units_by_id'] = {unit['id']: unit for unit in loaded_data['uom.uom']}

        loaded_data['taxes_by_id'] = {tax['id']: tax for tax in loaded_data['account.tax']}
        for tax in loaded_data['taxes_by_id'].values():
            tax['children_tax_ids'] = [loaded_data['taxes_by_id'][id] for id in tax['children_tax_ids']]

        for pricelist in loaded_data['product.pricelist']:
            if pricelist['id'] == self.config_id.pricelist_id.id:
                loaded_data['default_pricelist'] = pricelist
                break

        fiscal_position_by_id = {fpt['id']: fpt for fpt in self._get_pos_ui_account_fiscal_position_tax(
            self._loader_params_account_fiscal_position_tax())}
        for fiscal_position in loaded_data['account.fiscal.position']:
            fiscal_position['fiscal_position_taxes_by_id'] = {tax_id: fiscal_position_by_id[tax_id] for tax_id in
                                                              fiscal_position['tax_ids']}

        loaded_data['attributes_by_ptal_id'] = self._get_attributes_by_ptal_id()
        loaded_data['base_url'] = self.get_base_url()

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = [
            'res.company',
            'decimal.precision',
            'uom.uom',
            'res.country.state',
            'res.country',
            'res.lang',
            'account.tax',
            'pos.session',
            'pos.config',
            'pos.bill',
            'res.partner',
            'stock.picking.type',
            'res.users',
            'product.pricelist',
            'res.currency',
            'pos.category',
            'product.product',
            'product.packaging',
            'account.cash.rounding',
            'pos.payment.method',
            'account.fiscal.position',
        ]

        return models_to_load

    def _loader_params_res_company(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.company_id.id)],
                'fields': [
                    'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id',
                    'country_id', 'state_id', 'tax_calculation_rounding_method', 'nomenclature_id',
                    'point_of_sale_use_ticket_qr_code',
                ],
            }
        }

    def _get_pos_ui_res_company(self, params):
        company = self.env['res.company'].search_read(**params['search_params'])[0]
        params_country = self._loader_params_res_country()
        if company['country_id']:
            # TODO: this is redundant we have country_id and country
            params_country['search_params']['domain'] = [('id', '=', company['country_id'][0])]
            company['country'] = self.env['res.country'].search_read(**params_country['search_params'])[0]
        else:
            company['country'] = None

        return company

    def _loader_params_decimal_precision(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'digits']}}

    def _get_pos_ui_decimal_precision(self, params):
        decimal_precisions = self.env['decimal.precision'].search_read(**params['search_params'])
        return {dp['name']: dp['digits'] for dp in decimal_precisions}

    def _loader_params_uom_uom(self):
        return {'search_params': {'domain': [], 'fields': []}, 'context': {'active_test': False}}

    def _get_pos_ui_uom_uom(self, params):
        return self.env['uom.uom'].with_context(**params['context']).search_read(**params['search_params'])

    def _loader_params_res_country_state(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'country_id']}}

    def _get_pos_ui_res_country_state(self, params):
        return self.env['res.country.state'].search_read(**params['search_params'])

    def _loader_params_res_country(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'vat_label', 'code']}}

    def _get_pos_ui_res_country(self, params):
        return self.env['res.country'].search_read(**params['search_params'])

    def _loader_params_res_lang(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'code']}}

    def _get_pos_ui_res_lang(self, params):
        return self.env['res.lang'].search_read(**params['search_params'])

    def _loader_params_account_tax(self):
        return {
            'search_params': {
                'domain': [('company_id', '=', self.company_id.id)],
                'fields': [
                    'name', 'real_amount', 'price_include', 'include_base_amount', 'is_base_affected',
                    'amount_type', 'children_tax_ids'
                ],
            },
        }

    def _get_pos_ui_account_tax(self, params):
        taxes = self.env['account.tax'].search_read(**params['search_params'])
        # TODO: rename amount to real_amount in front end
        for tax in taxes:
            tax['amount'] = tax['real_amount']
            del tax['real_amount']
        return taxes

    def _loader_params_pos_session(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.id)],
                'fields': [
                    'id', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number',
                    'payment_method_ids', 'state', 'update_stock_at_closing', 'cash_register_balance_start'
                ],
            },
        }

    def _get_pos_ui_pos_session(self, params):
        return self.env['pos.session'].search_read(**params['search_params'])[0]

    def _loader_params_pos_config(self):
        return {'search_params': {'domain': [('id', '=', self.config_id.id)], 'fields': []}}

    def _get_pos_ui_pos_config(self, params):
        config = self.env['pos.config'].search_read(**params['search_params'])[0]
        config['use_proxy'] = config['is_posbox'] and (
                config['iface_electronic_scale'] or config['iface_print_via_proxy']
                or config['iface_scan_via_proxy'] or config['iface_customer_facing_display_via_proxy'])
        return config

    def _loader_params_pos_bill(self):
        return {'search_params': {'domain': [('id', 'in', self.config_id.default_bill_ids.ids)],
                                  'fields': ['name', 'value']}}

    def _get_pos_ui_pos_bill(self, params):
        return self.env['pos.bill'].search_read(**params['search_params'])

    def _loader_params_res_partner(self):
        return {
            'search_params': {
                'domain': [],
                'fields': [
                    'name', 'street', 'city', 'state_id', 'country_id', 'vat', 'lang', 'phone', 'zip', 'mobile',
                    'email',
                    'barcode', 'write_date', 'property_account_position_id', 'property_product_pricelist', 'parent_name'
                ],
            },
        }

    def _get_pos_ui_res_partner(self, params):
        if not self.config_id.limited_partners_loading:
            return self.env['res.partner'].search_read(**params['search_params'])
        partner_ids = [res[0] for res in self.config_id.get_limited_partners_loading()]
        # Need to search_read because get_limited_partners_loading
        # might return a partner id that is not accessible.
        params['search_params']['domain'] = [('id', 'in', partner_ids)]
        return self.env['res.partner'].search_read(**params['search_params'])

    def _loader_params_stock_picking_type(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.config_id.picking_type_id.id)],
                'fields': ['use_create_lots', 'use_existing_lots'],
            },
        }

    def _get_pos_ui_stock_picking_type(self, params):
        return self.env['stock.picking.type'].search_read(**params['search_params'])[0]

    def _loader_params_res_users(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.env.user.id)],
                'fields': ['name', 'groups_id'],
            },
        }

    def _get_pos_ui_res_users(self, params):
        user = self.env['res.users'].search_read(**params['search_params'])[0]
        user['role'] = 'manager' if any(id == self.config_id.group_pos_manager_id.id for id in user['groups_id']) else 'cashier'
        del user['groups_id']
        return user

    def _loader_params_product_pricelist(self):
        if self.config_id.use_pricelist:
            domain = [('id', 'in', self.config_id.available_pricelist_ids.ids)]
        else:
            domain = [('id', '=', self.config_id.pricelist_id.id)]
        return {'search_params': {'domain': domain, 'fields': ['name', 'display_name', 'discount_policy']}}

    def _product_pricelist_item_fields(self):
        return [
            'id',
            'product_tmpl_id',
            'product_id',
            'pricelist_id',
            'price_surcharge',
            'price_discount',
            'price_round',
            'price_min_margin',
            'price_max_margin',
            'company_id',
            'currency_id',
            'date_start',
            'date_end',
            'compute_price',
            'fixed_price',
            'percent_price',
            'base_pricelist_id',
            'base',
            'categ_id',
            'min_quantity',
        ]

    def _get_pos_ui_product_pricelist(self, params):
        pricelists = self.env['product.pricelist'].search_read(**params['search_params'])
        for pricelist in pricelists:
            pricelist['items'] = []

        pricelist_by_id = {pricelist['id']: pricelist for pricelist in pricelists}
        pricelist_item_domain = [('pricelist_id', 'in', [p['id'] for p in pricelists])]
        for item in self.env['product.pricelist.item'].search_read(pricelist_item_domain,
                                                                   self._product_pricelist_item_fields()):
            pricelist_by_id[item['pricelist_id'][0]]['items'].append(item)

        return pricelists

    def _loader_params_product_category(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'parent_id']}}

    def _get_pos_ui_product_category(self, params):
        categories = self.env['product.category'].search_read(**params['search_params'])
        category_by_id = {category['id']: category for category in categories}
        for category in categories:
            category['parent'] = category_by_id[category['parent_id'][0]] if category['parent_id'] else None
        return categories

    def _loader_params_res_currency(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.config_id.currency_id.id)],
                'fields': ['name', 'symbol', 'position', 'rounding', 'rate', 'decimal_places'],
            },
        }

    def _get_pos_ui_res_currency(self, params):
        return self.env['res.currency'].search_read(**params['search_params'])[0]

    def _loader_params_pos_category(self):
        domain = []
        if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
            domain = [('id', 'in', self.config_id.iface_available_categ_ids.ids)]

        return {'search_params': {'domain': domain,
                                  'fields': ['id', 'name', 'parent_id', 'child_id', 'write_date', 'has_image']}}

    def _get_pos_ui_pos_category(self, params):
        return self.env['pos.category'].search_read(**params['search_params'])

    def _loader_params_product_product(self):
        domain = [
            '&', '&', ('sale_ok', '=', True), ('available_in_pos', '=', True), '|',
            ('company_id', '=', self.config_id.company_id.id), ('company_id', '=', False)
        ]
        if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
            domain = AND([domain, [('pos_categ_id', 'in', self.config_id.iface_available_categ_ids.ids)]])
        if self.config_id.iface_tipproduct:
            domain = OR([domain, [('id', '=', self.config_id.tip_product_id.id)]])

        return {
            'search_params': {
                'domain': domain,
                'fields': [
                    'display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id', 'barcode',
                    'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id',
                    'tracking',
                    'write_date', 'available_in_pos', 'attribute_line_ids', 'active'
                ],
                'order': 'sequence,default_code,name',
            },
            'context': {'display_default_code': False},
        }

    def _process_pos_ui_product_product(self, products):
        """
        Modify the list of products to add the categories as well as adapt the lst_price
        :param products: a list of products
        """
        if self.config_id.currency_id != self.company_id.currency_id:
            for product in products:
                product['lst_price'] = self.company_id.currency_id._convert(product['lst_price'],
                                                                            self.config_id.currency_id,
                                                                            self.company_id, fields.Date.today())
        categories = self._get_pos_ui_product_category(self._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        for product in products:
            product['categ'] = product_category_by_id[product['categ_id'][0]]

    def _get_pos_ui_product_product(self, params):
        self = self.with_context(**params['context'])
        if not self.config_id.limited_products_loading:
            products = self.env['product.product'].search_read(**params['search_params'])
        else:
            products = self.config_id.get_limited_products_loading(params['search_params']['fields'])

        self._process_pos_ui_product_product(products)
        return products

    def _loader_params_product_packaging(self):
        return {
            'search_params': {
                'domain': [('barcode', 'not in', ['', False])],
                'fields': ['name', 'barcode', 'product_id', 'qty'],
            },
        }

    def _get_pos_ui_product_packaging(self, params):
        return self.env['product.packaging'].search_read(**params['search_params'])

    def _loader_params_account_cash_rounding(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.config_id.rounding_method.id)],
                'fields': ['name', 'rounding', 'rounding_method'],
            },
        }

    def _get_pos_ui_account_cash_rounding(self, params):
        return self.env['account.cash.rounding'].search_read(**params['search_params'])

    def _loader_params_pos_payment_method(self):
        vars = {
            'search_params': {
                'domain': ['|', ('active', '=', False), ('active', '=', True)],
                'fields': ['name', 'is_cash_count', 'use_payment_terminal', 'split_transactions', 'type', 'stripe_serial_number'],
                'order': 'is_cash_count desc, id',
            },
        }
        return vars

    def _get_pos_ui_pos_payment_method(self, params):
        return self.env['pos.payment.method'].search_read(**params['search_params'])

    def _loader_params_account_fiscal_position(self):
        return {'search_params': {'domain': [('id', 'in', self.config_id.fiscal_position_ids.ids)], 'fields': []}}

    def _get_pos_ui_account_fiscal_position(self, params):
        return self.env['account.fiscal.position'].search_read(**params['search_params'])

    def _loader_params_account_fiscal_position_tax(self):
        loaded_data = self._context.get('loaded_data')
        fps = loaded_data['account.fiscal.position']
        fiscal_position_tax_ids = sum([fpos['tax_ids'] for fpos in fps], [])
        return {'search_params': {'domain': [('id', 'in', fiscal_position_tax_ids)], 'fields': []}}

    def _get_pos_ui_account_fiscal_position_tax(self, params):
        return self.env['account.fiscal.position.tax'].search_read(**params['search_params'])

    def get_pos_ui_product_product_by_params(self, custom_search_params):
        """
        :param custom_search_params: a dictionary containing params of a search_read()
        """
        params = self._loader_params_product_product()
        # custom_search_params will take priority
        params['search_params'] = {**params['search_params'], **custom_search_params}
        products = self.env['product.product'].with_context(active_test=False).search_read(**params['search_params'])
        if len(products) > 0:
            self._process_pos_ui_product_product(products)
        return products

    def get_pos_ui_res_partner_by_params(self, custom_search_params):
        """
        :param custom_search_params: a dictionary containing params of a search_read()
        """
        params = self._loader_params_res_partner()
        # custom_search_params will take priority
        params['search_params'] = {**params['search_params'], **custom_search_params}
        partners = self.env['res.partner'].search_read(**params['search_params'])
        return partners

