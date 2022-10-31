from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


# import datetime

class Inventorys(models.Model):
    _inherit = "product.template"

    # sku = fields.Char('SKU')
    desc = fields.Char('Desc')
    mfg = fields.Many2many('wg.mfg.vendor', string='Mfg#', compute="_get_mfg", store=True)
    mfg_ven = fields.Text('Mfg#', compute="_combine_mfg_vendor")

    @api.depends('seller_ids')
    def _get_mfg(self):
        mfg_ids = []
        ven_ids = []
        for rec in self.seller_ids:
            if rec.mfg:
                mfg_ids.append(rec.mfg.id)
            if rec.name:
                ven_ids.append(rec.name.id)
        self.write({'mfg': [(6, 0, mfg_ids)], 'mfg_vende': [(6, 0, ven_ids)]})

    @api.depends('mfg', 'mfg_vende')
    def _combine_mfg_vendor(self):
        mfg_ven = '\n'
        for rec in self.seller_ids:
            if rec.mfg and rec.name:
                mfg_ven += rec.mfg.name + ' - ' + rec.name.name + '\n'
            elif rec.mfg:
                mfg_ven += rec.mfg.name + '\n'
        self.mfg_ven = mfg_ven

    Desc = fields.Char('Desc')
    upc = fields.Char('UPC')
    # dept = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    deptart = fields.Many2one('hr.department', ondelete='restrict', index=True, )
    class_invent = fields.Char('Class')
    class_inven = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    # prime_ved = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Prime Vend")
    # mfg_vend = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Mfg Vend")
    fineline = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Fineline")
    prime_vede = fields.Many2one('res.partner', ondelete='restrict', index=True, )
    mfg_vende = fields.Many2many('res.partner', ondelete='restrict', index=True, readonly=True, compute="_get_mfg")
    types = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    # store = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    company_id = fields.Many2one('res.company', ondelete='restrict', index=True, )
    sequence = fields.Char('Sequence')
    # instore = fields.Char('Instore')
    instores = fields.Many2many('res.company', ondelete='restrict', index=True, )
    pursku_ids = fields.Many2one('stock.picking')
    # quantity
    qut_on_hant = fields.Float('Qty On Hant ')
    commited_qty = fields.Float('Commited Qty')
    qty_on_order = fields.Float('Qty On Order')
    custbackorder = fields.Char('Custbackorder')
    location = fields.Char('Location')
    future_order = fields.Char('Future Order')
    company_onchange = fields.Many2one('res.company', ondelete='restrict', index=True,
                                       default=lambda self: self.env.company.id)
    sku_onchange = fields.Many2one('product.template', ondelete='restrict', index=True, )
    onchange_dept = fields.Many2one('hr.department', ondelete='restrict', index=True, )

    # stock level------------------------------
    order_point = fields.Float('Order Point ')
    min_order_ponit = fields.Float('Min Order Ponit')
    max_stock_level = fields.Float('Max Stock Level')
    safety_stock = fields.Float('Safety Stock')
    stockings_UM = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    stockings_UM_id = fields.Float('Stocking U/M"')
    stockings_UM_ids = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    standard_pack = fields.Float('Standard Pack')
    order_multiple = fields.Float('Order Multiple')

    raincheck_qty = fields.Float('Raincheck Qty')
    loc_table_id = fields.Many2one('stock.location', ondelete='restrict', index=True, )

    # purchasing

    purchasing_um = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Purchasing U/M")
    purchasing_um_id = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    order_indictor = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Order Indictor")
    # weight = fields.Float('Weight')
    weight_uom_id = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    # upc = fields.Integer('UPC')
    new_order_qty = fields.Float('New Order Qty')
    purch_conv_factor = fields.Float('*Purch Conv Factor')
    purch_decimal_pi = fields.Float('*Purch Decimal PI')
    min_of_std_pkgs = fields.Char('Min # of Std Pkgs')
    # secondary_vend = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    secondary_vends = fields.Many2one('res.partner', ondelete='restrict', index=True, )
    vend_stk = fields.Char('Vend Stk #')
    po_season = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="PO Season")

    # Dates
    date_added = fields.Date(string="Date Added")
    last_sale = fields.Date(string="Last Sale")
    last_receipt = fields.Date(string="Last Receipt")
    last_phy_inv = fields.Date(string="Last Phys Inv")
    catalog_date = fields.Char(string="Catalog Date")
    fixed_order_qty = fields.Float('Fixed Order QTY')
    altemate_ref = fields.Char('Altemate Ref')
    lost_sale = fields.Char('Lost Sale #/Units')  # Lost Sale #/Units
    bayouts = fields.Char('Bayouts #/Units')
    lost_scale_unit = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    bayout_unit = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])

    # pricing

    desiered_gp = fields.Float('Desiered GP')
    retail_old = fields.Float('Retail')
    catalog_retail = fields.Float('Catalog Retail')
    market_cost = fields.Char('Market Cost')
    synchronize_price = fields.Selection(
        [('Synchronize costs/prices', 'Y'), ('No do not synchronize', 'N'), ('use E4W', 'O')])
    synchronize_cost = fields.Selection(
        [('Synchronize costs/prices', 'Y'), ('No do not synchronize', 'N'), ('use E4W', 'O')])
    repl_chg = fields.Date(string="Repl Chg")
    retail_chg = fields.Date(string="Retail Chg")
    selling = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Selling")
    pricing = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Pricing")
    lumber_type = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], )
    level_price_overide = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Level Price Overide")
    rebate_group = fields.Char('Rebate Group')
    mfg_chg = fields.Monetary(string="Mfg Chg")
    repl_gp = fields.Float('Repl GP')
    # table
    price = fields.Char('Price')
    stock = fields.Char('Stock')
    alt = fields.Char('Alt')
    gp = fields.Char('GP %')
    tab_ids = fields.One2many('pricingtables', 'prc_ids', string="Trips and Tolls")

    # code

    price_rounding = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Pricing")
    tax_status = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    rop_protect = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    special_record = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    tally = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    loading_required = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    tax_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Tax Code")
    pos_return = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    updated_dept_data = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    seas_sale_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    bill_of_materials = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    lifo_pool_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    qty_break_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    product_code = fields.Char('Product Code')
    keep_stock_info = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    keep_price = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    count_promo_sale = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    vendor_back_order = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    promo_sale_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    popularity_code = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    print_label = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    bin_labels = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    discontinued = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    store_closeout = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    kit_record = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    discountable = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    has_alt_part = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    seas_promo = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    catalog_pg = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    keep_sale_history = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    keep_promo_history = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    amt_of_purchase_hist = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    exit_sale_history = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    ext_desc_groups = fields.Char()
    web = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    lot_item = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    promt_for_transfer = fields.Selection([('y', 'Y'), ('n', 'N'), ])
    multi_selling_user_code = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    multi_selling_user_codes = fields.Integer('Multi Selling User Code')

    # -----------

    user = fields.Char()
    expanded_user_one = fields.Char()
    expanded_user_two = fields.Char()
    expanded_user_three = fields.Char()
    expanded_user_four = fields.Char()
    expanded_a = fields.Char()
    expanded_a_one = fields.Char()
    expanded_a_two = fields.Char()
    expanded_a_three = fields.Char()
    expanded_a_four = fields.Char()
    expanded_b = fields.Char()
    expanded_b_one = fields.Char()
    expanded_b_two = fields.Char()
    expanded_b_three = fields.Char()
    expanded_b_four = fields.Char()
    expanded_c = fields.Char()
    expanded_c_one = fields.Char()
    expanded_c_two = fields.Char()
    expanded_c_three = fields.Char()
    expanded_c_four = fields.Char()
    expanded_d = fields.Char()
    expanded_d_one = fields.Char()
    expanded_d_two = fields.Char()
    expanded_d_three = fields.Char()
    expanded_d_four = fields.Char()

    # History tab

    cur_jan = fields.Float()
    cur_feb = fields.Float()
    cur_mar = fields.Float()
    cur_apr = fields.Float()
    cur_may = fields.Float()
    cur_jun = fields.Float()
    cur_july = fields.Float()
    cur_aug = fields.Float()
    cur_sep = fields.Float()
    cur_oct = fields.Float()
    cur_nov = fields.Float()
    cur_dec = fields.Float()

    curent_year = fields.Char(default=date.today().year)
    prev_year = fields.Char(default=date.today().year - 1)

    # -------------------------

    pre_jan = fields.Float()
    pre_feb = fields.Float()
    pre_mar = fields.Float()
    pre_apr = fields.Float()
    pre_may = fields.Float()
    pre_jun = fields.Float()
    pre_july = fields.Float()
    pre_aug = fields.Float()
    pre_sep = fields.Float()
    pre_oct = fields.Float()
    pre_nov = fields.Float()
    pre_dec = fields.Float()
    # jun_21 = fields.Integer()

    to_date = fields.Integer()
    last_per = fields.Date(string="Last Per")
    # year to date
    transactions = fields.Float()
    sale_units = fields.Float(compute='validation_sale', )
    sale = fields.Float(compute='total_sale_amount', )
    repl_cost = fields.Float()
    avg_cost = fields.Float()
    gross_pro = fields.Float()
    gross_pro_per = fields.Float()
    gmroi = fields.Float()
    his_qut_on_hant = fields.Float()
    his_commited_qty = fields.Float()
    his_qty_on_order = fields.Float()

    promo_unit = fields.Float()
    promo_sale = fields.Float()
    promo_cost = fields.Float()
    # doubt in prime vend
    prime_vend_history = fields.Many2one('res.partner', ondelete='restrict', index=True, )
    other_purch = fields.Char()
    kit_sales_unit = fields.Char()
    kit_sale = fields.Char()
    turns = fields.Float()
    his_future_order = fields.Char('Future Order')
    his_order_multiple = fields.Float('Order Multiple')
    his_popularity_code = fields.Selection([('y', 'Y'), ('n', 'N'), ])

    # last year
    last_year_sale_unit = fields.Char(compute='total_sale_last_year', )
    last_year_sale = fields.Float(compute='total_sales_amount_last_year', )
    last_year_repl_cost = fields.Float()
    last_year_avg_cost = fields.Float()
    last_year_gp = fields.Float()
    last_year_other_purchase = fields.Float()
    last_year_prime_vend = fields.Float()
    last_year_promo_units = fields.Float()
    on_hand_value = fields.Float()
    avg_sales_per_mont = fields.Float()
    stock_purchase_um = fields.Float()
    standard_pack = fields.Float()

    # note
    note_group = fields.Char()
    not_name = fields.Char()
    not_type = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    display_repeat = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    print_repeat = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    message = fields.Html()

    # load tab

    # quantites in load

    load_qut_on_hant = fields.Float()
    load_retail = fields.Float()
    load_list = fields.Float()
    load_repl_cost = fields.Float()
    mfg_cost = fields.Float()
    load_desired_gp = fields.Float()
    load_repl_gp = fields.Float()
    load_order_point = fields.Float()
    max_stk_level = fields.Float()

    # user code in load
    load_user = fields.Char()
    load_expanded_user_one = fields.Char()
    load_expanded_user_two = fields.Char()
    load_expanded_user_three = fields.Char()
    load_expanded_user_four = fields.Char()
    load_expanded_a = fields.Char()
    load_expanded_a_one = fields.Char()
    load_expanded_a_two = fields.Char()
    load_expanded_a_three = fields.Char()
    load_expanded_a_four = fields.Char()
    load_expanded_b = fields.Char()
    load_expanded_b_one = fields.Char()
    load_expanded_b_two = fields.Char()
    load_expanded_b_three = fields.Char()
    load_expanded_b_four = fields.Char()
    load_expanded_c = fields.Char()
    load_expanded_c_one = fields.Char()
    load_expanded_c_two = fields.Char()
    load_expanded_c_three = fields.Char()
    load_expanded_c_four = fields.Char()
    load_expanded_d = fields.Char()
    load_expanded_d_one = fields.Char()
    load_expanded_d_two = fields.Char()
    load_expanded_d_three = fields.Char()
    load_expanded_d_four = fields.Char()

    # purchasing in load

    load_stocking_um = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    load_stocking_um_ids = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    load_standard_pack = fields.Float()
    load_order_multiple = fields.Float()
    load_purchase_um = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    load_purchase_um_ids = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    order_indicator = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    load_weight = fields.Float()

    load_weight_units = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    load_min_of_std_pack = fields.Float()
    load_secondary_vend = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    load_vend_stk = fields.Char()
    load_po_season = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])

    # misc in load

    load_print_label = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    load_discountable = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    load_product_code = fields.Char()
    load_tax_status = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    load_special_record = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    load_cataloh_pg = fields.Char()
    load_seas_sales_code = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    load_location = fields.Char()
    load_pricing_um = fields.Selection([('Y', 'Y'), ('N', 'N'), ])

    # misc tab

    height = fields.Float()
    width = fields.Float()
    depth = fields.Float()
    weight_mic = fields.Float()
    weight_mic_units = fields.Many2one('uom.uom', ondelete='restrict', index=True, )
    cubes = fields.Float()
    cubes_unit = fields.Char()
    ebt = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    fsa = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    restricted_houres = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    age_restrict = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    special_fee_code = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    weighable = fields.Selection([('Y', 'Y'), ('N', 'N'), ])

    # vendor

    vend_ids = fields.One2many('inv_vendor_new', 'vend_ids', string="Trips and Tolls")

    # Pricing table
    units = fields.Char(default="EA")
    decimal_place = fields.Float()
    conversion = fields.Float()
    repl_cost = fields.Float()
    mfg_cost = fields.Float()
    avg_cost_pricing = fields.Float()
    mkt_cost = fields.Float()
    reail = fields.Float()
    list = fields.Char()
    promotion = fields.Float()
    price_one = fields.Float()
    price_two = fields.Float()
    price_three = fields.Float()
    price_four = fields.Float()
    price_five = fields.Float()

    # -----------
    units_stock = fields.Char()
    decimal_place_stock = fields.Float()
    conversion_stock = fields.Float()
    repl_cost_stock = fields.Float()
    mfg_cost_stock = fields.Float()
    avg_cost_stock = fields.Float()
    mkt_cost_stock = fields.Float()
    reail_stock = fields.Float()
    list_stock = fields.Char()
    promotion_stock = fields.Float()
    price_one_stock = fields.Float()
    price_two_stock = fields.Float()
    price_three_stock = fields.Float()
    price_four_stock = fields.Float()
    price_five_stock = fields.Float()
    # ----------
    units_alt = fields.Char()
    decimal_place_alt = fields.Float()
    conversion_alt = fields.Float()
    repl_cost_alt = fields.Float()
    mfg_cost_alt = fields.Float()
    avg_cost_alt = fields.Float()
    mkt_cost_alt = fields.Float()
    reail_alt = fields.Float()
    list_alt = fields.Char()
    promotion_alt = fields.Float()
    price_one_alt = fields.Float()
    price_two_alt = fields.Float()
    price_three_alt = fields.Float()
    price_four_alt = fields.Float()
    price_five_alt = fields.Float()
    # -------
    units_gp = fields.Char()
    decimal_place_gp = fields.Float()
    conversion_gp = fields.Float()
    repl_cost_gp = fields.Float()
    mfg_cost_gp = fields.Float()
    avg_cost_gp = fields.Float()
    mkt_cost_gp = fields.Float()
    reail_gp = fields.Float()
    list_gp = fields.Char()
    promotion_gp = fields.Float()
    price_one_gp = fields.Float()
    price_two_gp = fields.Float()
    price_three_gp = fields.Float()
    price_four_gp = fields.Float()
    price_five_gp = fields.Float()

    location_quan_id = fields.One2many('stock.quant', 'loc_quan_ids', string="Location")

    # -----------
    # units = fields.Char()
    # decimal_place = fields.Float()
    # conversion = fields.Float()
    # repl_cost = fields.Float()
    # mfg_cost = fields.Float()
    # avg_cost = fields.Float()
    # mkt_cost = fields.Float()
    # reail = fields.Float()
    # list = fields.Char()
    # promotion = fields.Float()
    # price_one = fields.Float()
    # price_two = fields.Float()
    # price_three = fields.Float()
    # price_four = fields.Float()
    # price_five = fields.Float()

    # validate all
    def validate_float(self, float_value, val):
        if float_value:
            if len(str(float_value)) > 12:
                raise ValidationError("10 digits be allowed in %s" % val)

    # validate 5 digit
    def validate_float_five(self, float_value, val):
        if float_value:
            # print("*****************************************************", len(str(float_value)),float_value)
            if len(str(float_value)) > 7:
                raise ValidationError("5 digits be allowed in %s" % val)

    @api.onchange('company_id')
    def validate_store(self):
        if self.company_id:
            selected_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
            if self.company_id not in selected_companies:
                raise ValidationError("please select the company you are logged.")

    # Stocking

    # validate 5 digit validation

    @api.constrains('weight', 'purch_conv_factor', 'purch_decimal_pi')
    def validate_con_stocking_five_digit(self):
        # if self.weight:
        #     val = "Weight"
        #     self.validate_float_five(self.weight, val)
        if self.purch_conv_factor:
            val = "*Purch Conv Factor"
            self.validate_float_five(self.purch_conv_factor, val)
        if self.purch_decimal_pi:
            val = "*Purch Decimal PI"
            self.validate_float_five(self.purch_decimal_pi, val)

    # onchange 5 digit validation

    @api.onchange('weight', 'purch_conv_factor', 'purch_decimal_pi')
    def validate_oc_stocking_five_digit(self):
        # if self.weight:
        #     val = "Weight"
        #     self.validate_float_five(self.weight, val)
        if self.purch_conv_factor:
            val = "*Purch Conv Factor"
            self.validate_float_five(self.purch_conv_factor, val)
        if self.purch_decimal_pi:
            val = "*Purch Decimal PI"
            self.validate_float_five(self.purch_decimal_pi, val)

    # 10 digit validation

    @api.constrains('qut_on_hant', 'commited_qty', 'qty_on_order', 'order_point', 'min_order_ponit', 'safety_stock',
                    'standard_pack', 'order_multiple', 'raincheck_qty', 'raincheck_qty', 'new_order_qty',
                    'fixed_order_qty')
    def validate_con_qut_on_hant(self):
        if self.qut_on_hant:
            val = "Qty On Hand"
            self.validate_float(self.qut_on_hant, val)
        if self.commited_qty:
            val = "Commited Qty"
            self.validate_float(self.commited_qty, val)

        if self.qty_on_order:
            val = "Qty On Order"
            self.validate_float(self.qty_on_order, val)
        if self.order_point:
            val = "Order Point"
            self.validate_float(self.order_point, val)
        if self.min_order_ponit:
            val = "Min Order Point"
            self.validate_float(self.min_order_ponit, val)
        if self.safety_stock:
            val = "Safety Stock"
            self.validate_float(self.safety_stock, val)
        if self.standard_pack:
            val = "Standard Pack"
            self.validate_float(self.standard_pack, val)
        if self.order_multiple:
            val = "Order Multiple"
            self.validate_float(self.order_multiple, val)
        if self.raincheck_qty:
            val = "Raincheck Qty"
            self.validate_float(self.raincheck_qty, val)
        if self.new_order_qty:
            val = "New Order Qty"
            self.validate_float(self.new_order_qty, val)
        if self.fixed_order_qty:
            val = "Fixed Order QTY"
            self.validate_float(self.fixed_order_qty, val)

    # onchange 10 digit validation

    @api.onchange('qut_on_hant', 'commited_qty', 'qty_on_order', 'order_point', 'min_order_ponit', 'safety_stock',
                  'standard_pack', 'order_multiple', 'raincheck_qty', 'raincheck_qty', 'new_order_qty',
                  'fixed_order_qty')
    def validate_oc_ten_digit(self):
        if self.qut_on_hant:
            val = "Qty On Hand"
            self.validate_float(self.qut_on_hant, val)
        if self.commited_qty:
            val = "Commited Qty"
            self.validate_float(self.commited_qty, val)

        if self.qty_on_order:
            val = "Qty On Order"
            self.validate_float(self.qty_on_order, val)
        if self.order_point:
            val = "Order Point"
            self.validate_float(self.order_point, val)
        if self.min_order_ponit:
            val = "Min Order Point"
            self.validate_float(self.min_order_ponit, val)
        if self.safety_stock:
            val = "Safety Stock"
            self.validate_float(self.safety_stock, val)
        if self.standard_pack:
            val = "Standard Pack"
            self.validate_float(self.standard_pack, val)
        if self.order_multiple:
            val = "Order Multiple"
            self.validate_float(self.order_multiple, val)
        if self.raincheck_qty:
            val = "Raincheck Qty"
            self.validate_float(self.raincheck_qty, val)
        if self.new_order_qty:
            val = "New Order Qty"
            self.validate_float(self.new_order_qty, val)
        if self.fixed_order_qty:
            val = "Fixed Order QTY"
            self.validate_float(self.fixed_order_qty, val)

    # pricing

    # 5 digits
    @api.constrains('decimal_place', 'decimal_place_stock', 'repl_cost_gp', 'decimal_place_alt', 'decimal_place_gp',
                    'mkt_cost_gp', 'mfg_cost_gp', 'avg_cost_gp', 'reail_gp', 'promotion_gp', 'price_one_gp',
                    'price_two_gp', 'price_three_gp', 'price_four_gp', 'price_five_gp', 'desiered_gp', 'repl_gp')
    def validate_con_pricing_five_digit(self):
        if self.decimal_place:
            val = "Decimal Place Price"
            self.validate_float_five(self.decimal_place, val)
        if self.decimal_place_stock:
            val = "Decimal Place Stock"
            self.validate_float_five(self.decimal_place_stock, val)

        if self.decimal_place_alt:
            val = "Decimal Place Alt"
            self.validate_float_five(self.decimal_place_alt, val)
        if self.repl_cost_gp:
            val = "Repl Cost GP%"
            self.validate_float_five(self.repl_cost_gp, val)
        if self.decimal_place_gp:
            val = "Decimal Place GP"
            self.validate_float_five(self.decimal_place_gp, val)
        if self.mkt_cost_gp:
            val = "Mkt Cost GP"
            self.validate_float_five(self.mkt_cost_gp, val)
        if self.mfg_cost_gp:
            val = "Mfg Cost GP"
            self.validate_float_five(self.mfg_cost_gp, val)
        if self.avg_cost_gp:
            val = "Avg Cost GP"
            self.validate_float_five(self.avg_cost_gp, val)
        if self.reail_gp:
            val = "Reail GP"
            self.validate_float_five(self.reail_gp, val)
        if self.promotion_gp:
            val = "Promotion GP"
            self.validate_float_five(self.promotion_gp, val)
        if self.price_one_gp:
            val = "Price 1 GP"
            self.validate_float_five(self.price_one_gp, val)
        if self.price_two_gp:
            val = "Price 2 GP"
            self.validate_float_five(self.price_two_gp, val)
        if self.price_three_gp:
            val = "Price 3 GP"
            self.validate_float_five(self.price_three_gp, val)
        if self.price_four_gp:
            val = "Price 4 GP"
            self.validate_float_five(self.price_four_gp, val)
        if self.price_five_gp:
            val = "Price 5"
            self.validate_float_five(self.price_five_gp, val)
        if self.desiered_gp:
            val = "Desired GP %"
            self.validate_float_five(self.desiered_gp, val)
        if self.repl_gp:
            val = "Repl GP%"
            self.validate_float_five(self.repl_gp, val)

    # onchange 5 digit

    @api.onchange('decimal_place', 'decimal_place_stock', 'repl_cost_gp', 'decimal_place_alt', 'decimal_place_gp',
                  'mkt_cost_gp', 'mfg_cost_gp', 'avg_cost_gp', 'reail_gp', 'promotion_gp', 'price_one_gp',
                  'price_two_gp', 'price_three_gp', 'price_four_gp', 'price_five_gp', 'desiered_gp', 'repl_gp')
    def validate_oc_pricing_five_digit(self):
        if self.decimal_place:
            val = "Decimal Place Price"
            self.validate_float_five(self.decimal_place, val)
        if self.decimal_place_stock:
            val = "Decimal Place Stock"
            self.validate_float_five(self.decimal_place_stock, val)

        if self.decimal_place_alt:
            val = "Decimal Place Alt"
            self.validate_float_five(self.decimal_place_alt, val)
        if self.repl_cost_gp:
            val = "Repl Cost GP%"
            self.validate_float_five(self.repl_cost_gp, val)
        if self.decimal_place_gp:
            val = "Decimal Place GP"
            self.validate_float_five(self.decimal_place_gp, val)
        if self.mkt_cost_gp:
            val = "Mkt Cost GP"
            self.validate_float_five(self.mkt_cost_gp, val)
        if self.mfg_cost_gp:
            val = "Mfg Cost GP"
            self.validate_float_five(self.mfg_cost_gp, val)
        if self.avg_cost_gp:
            val = "Avg Cost GP"
            self.validate_float_five(self.avg_cost_gp, val)
        if self.reail_gp:
            val = "Reail GP"
            self.validate_float_five(self.reail_gp, val)
        if self.promotion_gp:
            val = "Promotion GP"
            self.validate_float_five(self.promotion_gp, val)
        if self.price_one_gp:
            val = "Price 1 GP"
            self.validate_float_five(self.price_one_gp, val)
        if self.price_two_gp:
            val = "Price 2 GP"
            self.validate_float_five(self.price_two_gp, val)
        if self.price_three_gp:
            val = "Price 3 GP"
            self.validate_float_five(self.price_three_gp, val)
        if self.price_four_gp:
            val = "Price 4 GP"
            self.validate_float_five(self.price_four_gp, val)
        if self.price_five_gp:
            val = "Price 5"
            self.validate_float_five(self.price_five_gp, val)
        if self.desiered_gp:
            val = "Desired GP %"
            self.validate_float_five(self.desiered_gp, val)
        if self.repl_gp:
            val = "Repl GP%"
            self.validate_float_five(self.repl_gp, val)

    # 10 digit

    @api.constrains('repl_cost', 'repl_cost_stock', 'repl_cost_alt', 'mfg_cost', 'mfg_cost_stock', 'mfg_cost_alt',
                    'avg_cost_pricing', 'avg_cost_stock', 'avg_cost_alt', 'mkt_cost', 'mkt_cost_stock', 'mkt_cost_alt',
                    'reail', 'reail_stock', 'reail_alt')
    def validate_con_pricing_one(self):
        if self.repl_cost:
            val = "Repl Cost Pricing"
            self.validate_float(self.repl_cost, val)
        if self.repl_cost_stock:
            val = "Repl Cost Stock"
            self.validate_float(self.repl_cost_stock, val)

        if self.repl_cost_alt:
            val = "Repl Cost Alt"
            self.validate_float(self.repl_cost_alt, val)
        if self.mfg_cost:
            val = "Mfg Cost Price"
            self.validate_float(self.mfg_cost, val)
        if self.mfg_cost_stock:
            val = "Mfg Cost Stock"
            self.validate_float(self.mfg_cost_stock, val)
        if self.mfg_cost_alt:
            val = "Mfg Cost Alt"
            self.validate_float(self.mfg_cost_alt, val)
        if self.avg_cost_pricing:
            val = "Avg Cost Pricing"
            self.validate_float(self.avg_cost_pricing, val)
        if self.avg_cost_stock:
            val = "Avg Cost Stock"
            self.validate_float(self.avg_cost_stock, val)
        if self.avg_cost_alt:
            val = "Avg Cost Alt"
            self.validate_float(self.avg_cost_alt, val)
        if self.mkt_cost:
            val = "Mkt Cost Pricing"
            self.validate_float(self.mkt_cost, val)
        if self.mkt_cost_stock:
            val = "Mkt Cost Stock"
            self.validate_float(self.mkt_cost_stock, val)
        if self.mkt_cost_alt:
            val = "Mkt Cost Alt"
            self.validate_float(self.mkt_cost_alt, val)
        if self.reail:
            val = "Reail Pricing"
            self.validate_float(self.reail, val)
        if self.reail_stock:
            val = "Reail Stock"
            self.validate_float(self.reail_stock, val)
        if self.reail_alt:
            val = "Reail Alt"
            self.validate_float(self.reail_alt, val)

    # 10 digit two
    @api.constrains('promotion', 'promotion_stock', 'promotion_alt', 'price_one', 'price_one_stock', 'price_one_alt',
                    'price_two', 'price_two_stock', 'price_two_alt', 'price_three', 'price_three_stock',
                    'price_three_alt', 'price_four', 'price_four_stock', 'price_four_alt', 'price_five',
                    'price_five_stock', 'price_five_alt')
    def validate_con_pricing_two(self):
        if self.promotion:
            val = "Promotion Pricing"
            self.validate_float(self.promotion, val)
        if self.promotion_stock:
            val = "Promotion Stock"
            self.validate_float(self.promotion_stock, val)

        if self.promotion_alt:
            val = "Promotion Alt"
            self.validate_float(self.promotion_alt, val)
        if self.price_one:
            val = "Price 1 Priceing"
            self.validate_float(self.price_one, val)
        if self.price_one_stock:
            val = "Price 1 Stock"
            self.validate_float(self.price_one_stock, val)
        if self.price_one_alt:
            val = "Price 1 Alt"
            self.validate_float(self.price_one_alt, val)
        if self.price_two:
            val = "Price 2 Pricing"
            self.validate_float(self.price_two, val)
        if self.price_two_stock:
            val = "Price 2 Stock"
            self.validate_float(self.price_two_stock, val)
        if self.price_two_alt:
            val = "Price 2 Alt"
            self.validate_float(self.price_two_alt, val)
        if self.price_three:
            val = "Price 3 Pricing"
            self.validate_float(self.price_three, val)
        if self.price_three_stock:
            val = "Price 3 Stock"
            self.validate_float(self.price_three_stock, val)
        if self.price_three_alt:
            val = "Price 3 Alt"
            self.validate_float(self.price_three_alt, val)
        if self.price_four:
            val = "Price 4 Pricing"
            self.validate_float(self.price_four, val)
        if self.price_four_stock:
            val = "Price 4 Stock"
            self.validate_float(self.price_four_stock, val)
        if self.price_four_alt:
            val = "Price 4 Alt"
            self.validate_float(self.price_four_alt, val)
        if self.price_five:
            val = "Price 5 Pricing"
            self.validate_float(self.price_five, val)
        if self.price_five_stock:
            val = "Price 5 Stock"
            self.validate_float(self.price_five_stock, val)
        if self.price_five_alt:
            val = "Price 5 Alt"
            self.validate_float(self.price_five_alt, val)

    # 10 digit three
    @api.constrains('retail_old', 'catalog_retail', 'market_cost', 'mfg_chg')
    def validate_con_pricing_three(self):
        if self.retail_old:
            val = "Retail(old)"
            self.validate_float(self.retail_old, val)
        if self.catalog_retail:
            val = "Catalog Retail"
            self.validate_float(self.catalog_retail, val)

        if self.market_cost:
            val = "*Market Cost"
            self.validate_float(self.market_cost, val)
        if self.mfg_chg:
            val = "Mfg Chg"
            self.validate_float(self.mfg_chg, val)

    # onchange 10 digit

    @api.onchange('repl_cost', 'repl_cost_stock', 'repl_cost_alt', 'mfg_cost', 'mfg_cost_stock', 'mfg_cost_alt',
                  'avg_cost_pricing', 'avg_cost_stock', 'avg_cost_alt', 'mkt_cost', 'mkt_cost_stock', 'mkt_cost_alt',
                  'reail', 'reail_stock', 'reail_alt')
    def validate_oc_pricing_one(self):
        if self.repl_cost:
            val = "Repl Cost Pricing"
            self.validate_float(self.repl_cost, val)
        if self.repl_cost_stock:
            val = "Repl Cost Stock"
            self.validate_float(self.repl_cost_stock, val)

        if self.repl_cost_alt:
            val = "Repl Cost Alt"
            self.validate_float(self.repl_cost_alt, val)
        if self.mfg_cost:
            val = "Mfg Cost Price"
            self.validate_float(self.mfg_cost, val)
        if self.mfg_cost_stock:
            val = "Mfg Cost Stock"
            self.validate_float(self.mfg_cost_stock, val)
        if self.mfg_cost_alt:
            val = "Mfg Cost Alt"
            self.validate_float(self.mfg_cost_alt, val)
        if self.avg_cost_pricing:
            val = "Avg Cost Pricing"
            self.validate_float(self.avg_cost_pricing, val)
        if self.avg_cost_stock:
            val = "Avg Cost Stock"
            self.validate_float(self.avg_cost_stock, val)
        if self.avg_cost_alt:
            val = "Avg Cost Alt"
            self.validate_float(self.avg_cost_alt, val)
        if self.mkt_cost:
            val = "Mkt Cost Pricing"
            self.validate_float(self.mkt_cost, val)
        if self.mkt_cost_stock:
            val = "Mkt Cost Stock"
            self.validate_float(self.mkt_cost_stock, val)
        if self.mkt_cost_alt:
            val = "Mkt Cost Alt"
            self.validate_float(self.mkt_cost_alt, val)
        if self.reail:
            val = "Reail Pricing"
            self.validate_float(self.reail, val)
        if self.reail_stock:
            val = "Reail Stock"
            self.validate_float(self.reail_stock, val)
        if self.reail_alt:
            val = "Reail Alt"
            self.validate_float(self.reail_alt, val)

    # 10 digit two
    @api.onchange('promotion', 'promotion_stock', 'promotion_alt', 'price_one', 'price_one_stock', 'price_one_alt',
                  'price_two', 'price_two_stock', 'price_two_alt', 'price_three', 'price_three_stock',
                  'price_three_alt', 'price_four', 'price_four_stock', 'price_four_alt', 'price_five',
                  'price_five_stock', 'price_five_alt')
    def validate_oc_pricing_two(self):
        if self.promotion:
            val = "Promotion Pricing"
            self.validate_float(self.promotion, val)
        if self.promotion_stock:
            val = "Promotion Stock"
            self.validate_float(self.promotion_stock, val)

        if self.promotion_alt:
            val = "Promotion Alt"
            self.validate_float(self.promotion_alt, val)
        if self.price_one:
            val = "Price 1 Priceing"
            self.validate_float(self.price_one, val)
        if self.price_one_stock:
            val = "Price 1 Stock"
            self.validate_float(self.price_one_stock, val)
        if self.price_one_alt:
            val = "Price 1 Alt"
            self.validate_float(self.price_one_alt, val)
        if self.price_two:
            val = "Price 2 Pricing"
            self.validate_float(self.price_two, val)
        if self.price_two_stock:
            val = "Price 2 Stock"
            self.validate_float(self.price_two_stock, val)
        if self.price_two_alt:
            val = "Price 2 Alt"
            self.validate_float(self.price_two_alt, val)
        if self.price_three:
            val = "Price 3 Pricing"
            self.validate_float(self.price_three, val)
        if self.price_three_stock:
            val = "Price 3 Stock"
            self.validate_float(self.price_three_stock, val)
        if self.price_three_alt:
            val = "Price 3 Alt"
            self.validate_float(self.price_three_alt, val)
        if self.price_four:
            val = "Price 4 Pricing"
            self.validate_float(self.price_four, val)
        if self.price_four_stock:
            val = "Price 4 Stock"
            self.validate_float(self.price_four_stock, val)
        if self.price_four_alt:
            val = "Price 4 Alt"
            self.validate_float(self.price_four_alt, val)
        if self.price_five:
            val = "Price 5 Pricing"
            self.validate_float(self.price_five, val)
        if self.price_five_stock:
            val = "Price 5 Stock"
            self.validate_float(self.price_five_stock, val)
        if self.price_five_alt:
            val = "Price 5 Alt"
            self.validate_float(self.price_five_alt, val)

    # 10 digit three
    @api.onchange('retail_old', 'catalog_retail', 'market_cost', 'mfg_chg')
    def validate_oc_pricing_three(self):
        if self.retail_old:
            val = "Retail(old)"
            self.validate_float(self.retail_old, val)
        if self.catalog_retail:
            val = "Catalog Retail"
            self.validate_float(self.catalog_retail, val)

        if self.market_cost:
            val = "*Market Cost"
            self.validate_float(self.market_cost, val)
        if self.mfg_chg:
            val = "Mfg Chg"
            self.validate_float(self.mfg_chg, val)

    # Total sale order

    def validation_sale(self):

        todays_date = date.today().replace(month=1, day=1)
        total_sales = self.env['sale.order'].search([('state', '=', 'sale'), ('date_order', '>=', todays_date)])
        self.sale_units = len(total_sales)

    # Total amount

    def total_sale_amount(self):

        todays_date = date.today().replace(month=1, day=1)

        amount = 0
        sales_invoice = self.env['sale.order'].search(
            [('state', '=', 'sale'), ('state', '!=', 'draft'), ('state', '!=', 'cancel'),
             ('date_order', '>=', todays_date)])
        if sales_invoice:
            for sale in sales_invoice:
                amount += sale.amount_total

        self.sale = amount

    # Total sale order in last year

    def total_sale_last_year(self):
        curr_year = date.today()
        las_year = curr_year.year - 1
        last_year_jan = date.today().replace(year=las_year, month=1, day=1)

        last_year_dec = date.today().replace(year=las_year, month=12, day=31)
        last_year_sale = self.env['sale.order'].search(
            [('date_order', '>=', last_year_jan), ('date_order', '<', last_year_dec), ('state', '=', 'sale')])

        self.last_year_sale_unit = len(last_year_sale)

    # Total amount in last year
    # @api.onchange('mfg_vende')
    def total_sales_amount_last_year(self):
        curr_year = date.today()
        tot_amount = 0
        las_year = curr_year.year - 1
        last_year_january = date.today().replace(year=las_year, month=1, day=1)
        last_year_december = date.today().replace(year=las_year, month=12, day=31)
        last_year_all_sale = self.env['sale.order'].search(
            [('date_order', '>=', last_year_january), ('date_order', '<', last_year_december), ('state', '=', 'sale'),
             ('state', '!=', 'draft'), ('state', '!=', 'cancel')])
        if last_year_all_sale:
            for sal in last_year_all_sale:
                tot_amount += sal.amount_total

        self.last_year_sale = tot_amount

    # @api.constrains('prime_vede')
    # def asdf(self):
    #     if self.prime_vede:
    #         asd = self.env['res.partner'].search([('id', '=', self.prime_vede.id)])
    #         for i in self.ids:
    #             valu = i
    #             dupli = self.env['inv_vendor_new'].search(
    #                 [('partner_id', '=', self.prime_vede.id), ('vend_ids', '=', valu),
    #                  ('vendor_name', '=', self.prime_vede.name)])
    #             if len(dupli) == 0:
    #                 vals = [(0, 0, {'partner_id': asd.id, 'vendor_name': asd.name, 'vend_ids': valu})]
    #                 self.update({'vend_ids': vals})

    # @api.constrains('prime_vede')
    # def asdf(self):
    #     if self.prime_vede:
    #         asd = self.env['res.partner'].search([('id', '=', self.prime_vede.id)])
    #         for i in self.ids:
    #             valu = i
    #             dupli = self.env['inv_vendor_new'].search(
    #                 [('partner_id', '=', self.prime_vede.id), ('vend_ids', '=', valu),
    #                  ('vendor_name', '=', self.prime_vede.name)])
    #             recs = self.env['inv_vendor_new'].search(
    #                 [('partner_id', '!=', self.prime_vede.id), ('vend_ids', '=', valu),
    #                  ('on_create', '=', True)]).unlink()

    #             if len(dupli) == 0:
    #                 vals = [
    #                     (0, 0, {'partner_id': asd.id, 'vendor_name': asd.name, 'vend_ids': valu, 'on_create': True})]
    #                 self.update({'vend_ids': vals})


    @api.onchange('sku_onchange')
    def _store_change(self):
        # if self.company_onchange
        # store_data = self.env['product.template'].search([('id', '=', self.sku_onchange.id), ('company_id.id', '=', self.company_onchange.id)],
        #                                                  limit=1)

        if not self.company_onchange:
            raise ValidationError("Filter BY Store is Empty")
        else:
            store_datas = self.env['product.template'].search([('id', '=', self.sku_onchange.id), ])


            self.name = store_datas.name
            self.desc = store_datas.desc
            # self.mfg = store_datas.mfg
            self.upc = store_datas.upc
            self.sequence = store_datas.sequence
            self.deptart = store_datas.deptart
            self.class_invent = store_datas.class_invent
            self.types = store_datas.types
            self.instores = store_datas.instores
            self.prime_vede = store_datas.prime_vede
            self.mfg_vende = store_datas.mfg_vende
            self.company_id = store_datas.company_id
            self.class_invent = store_datas.class_invent
            self.types = store_datas.types
            self.instores = store_datas.instores


            self.load_retail = store_datas.load_retail
            self.qty_available = store_datas.qty_available
            self.list_price = store_datas.list_price
            self.load_repl_cost = store_datas.load_repl_cost
            self.mfg_cost = store_datas.mfg_cost


            # Fields in note book tab

            self.qty_available = store_datas.qty_available
            self.qty_available = store_datas.qty_available
            self.purchased_product_qty = store_datas.purchased_product_qty
            self.order_point = store_datas.order_point
            self.reordering_min_qty = store_datas.reordering_min_qty
            self.reordering_max_qty = store_datas.reordering_max_qty
            self.safety_stock = store_datas.safety_stock
            self.stockings_UM_ids = store_datas.stockings_UM_ids
            self.standard_pack = store_datas.standard_pack
            self.order_multiple = store_datas.order_multiple
            self.raincheck_qty = store_datas.raincheck_qty
            self.purchasing_um_id = store_datas.purchasing_um_id
            self.weight = store_datas.weight
            self.weight_uom_id = store_datas.weight_uom_id
            self.new_order_qty = store_datas.new_order_qty
            self.purch_conv_factor = store_datas.purch_conv_factor
            self.purch_decimal_pi = store_datas.purch_decimal_pi
            self.min_of_std_pkgs = store_datas.min_of_std_pkgs
            self.secondary_vends = store_datas.secondary_vends


            self.date_added = store_datas.date_added
            self.last_sale = store_datas.last_sale
            self.last_receipt = store_datas.last_receipt
            self.last_phy_inv = store_datas.last_phy_inv
            self.catalog_date = store_datas.catalog_date
            self.fixed_order_qty = store_datas.fixed_order_qty
            self.altemate_ref = store_datas.altemate_ref

            self.name = store_datas.name
            self.desc = store_datas.desc
            # self.mfg = store_datas.mfg
            self.upc = store_datas.upc
            self.sequence = store_datas.sequence
            self.deptart = store_datas.deptart
            self.class_invent = store_datas.class_invent
            self.types = store_datas.types
            self.instores = store_datas.instores
            self.prime_vede = store_datas.prime_vede
            self.mfg_vende = store_datas.mfg_vende
            self.company_id = store_datas.company_id

    @api.onchange('company_onchange')
    def _company_change(self):
        # if self.company_onchange
        # store_data = self.env['product.template'].search([('name', '=', self.sku_onchange.name),('company_id', '=', self.company_onchange.id),],
        #                                                  limit=1)
        company_onchange_data = self.env['product.template'].search([('name', '=', self.sku_onchange.name),('company_id', '=', self.company_onchange.id)],
                                                         limit=1)

        self.name = company_onchange_data.name
        self.desc = company_onchange_data.desc
        # self.mfg = store_data.mfg
        self.upc = company_onchange_data.upc
        self.sequence = company_onchange_data.sequence
        self.deptart = company_onchange_data.deptart
        self.class_invent = company_onchange_data.class_invent
        self.types = company_onchange_data.types
        self.instores = company_onchange_data.instores
        self.prime_vede = company_onchange_data.prime_vede
        self.mfg_vende = company_onchange_data.mfg_vende
        self.company_id = company_onchange_data.company_id
        self.class_invent = company_onchange_data.class_invent
        self.types = company_onchange_data.types
        self.instores = company_onchange_data.instores


        self.load_retail = company_onchange_data.load_retail
        self.qty_available = company_onchange_data.qty_available
        self.list_price = company_onchange_data.list_price
        self.load_repl_cost = company_onchange_data.load_repl_cost
        self.mfg_cost = company_onchange_data.mfg_cost
        # self.company_id = store_data.company_id


    @api.onchange('onchange_dept')
    def _onchange_dept(self):
        # if self.onchange_dept
        # store_data = self.env['product.template'].search([('name', '=', self.sku_onchange.name),('company_id', '=', self.company_onchange.id),],
        #                                                  limit=1)
        store_data = self.env['product.template'].search([('name', '=', self.sku_onchange.name),('company_id', '=', self.company_onchange.id),('deptart', '=', self.onchange_dept.id)],
                                                         limit=1)

        self.name = store_data.name
        self.desc = store_data.desc
        # self.mfg = store_data.mfg
        self.upc = store_data.upc
        self.sequence = store_data.sequence
        self.deptart = store_data.deptart
        self.class_invent = store_data.class_invent
        self.types = store_data.types
        self.instores = store_data.instores
        self.prime_vede = store_data.prime_vede
        self.mfg_vende = store_data.mfg_vende
        self.company_id = store_data.company_id
        self.class_invent = store_data.class_invent
        self.types = store_data.types
        self.instores = store_data.instores


        self.load_retail = store_data.load_retail
        self.qty_available = store_data.qty_available
        self.list_price = store_data.list_price
        self.load_repl_cost = store_data.load_repl_cost
        self.mfg_cost = store_data.mfg_cost



    @api.model
    def create(self, vals):

        valdate_sku = self.env['product.template'].search(
            [('name', '=', vals['name']), ('company_id.id', '=', vals['company_id']),('deptart', '=', vals['deptart'])], limit=1)

        if valdate_sku:
            raise ValidationError("Product Already Exists")
        else:
            return super(Inventorys, self).create(vals)


    def action_student_schedules(self):
        pass


# Table in pricing tab
class Pricetable(models.Model):
    _name = "pricingtables"
    units = fields.Char(string="Units")
    price = fields.Char(string="Pricing")
    stock = fields.Char(string="Stock")
    alt = fields.Char(string="Alt")
    gp = fields.Char(string="GP %")
    blk = fields.Char()
    prc_ids = fields.Many2one('product.template')


# Table for vendor
class inv_vendor(models.Model):
    _name = "inv_vendor"


class inv_vendornew(models.Model):
    _name = "inv_vendor_new"
    partner_id = fields.Integer()
    vendor_code = fields.Char()
    vendor_name = fields.Char()
    vendor_part = fields.Char()
    vendor_order_multi = fields.Float()
    min_od_ord_mult = fields.Float()
    unit_to_order_by = fields.Float()
    vend_cost = fields.Float()
    po_back_order = fields.Char()
    last_pur_cost = fields.Float()
    last_cost_change = fields.Float()
    last_pur_qty = fields.Float()
    last_pur_date = fields.Date()
    last_po_number = fields.Char()
    discontinued = fields.Char()
    store_closeout = fields.Char()
    desc_line_one = fields.Char()
    desc_line_two = fields.Char()
    on_create = fields.Boolean()
    vend_ids = fields.Many2one('product.template')


class inv_vendor(models.Model):
    _inherit = "stock.quant"

    loc_quan_ids = fields.Many2one('product.template')


class SupplierInherit(models.Model):
    _inherit = "product.supplierinfo"

    mfg = fields.Many2one('wg.mfg.vendor')
    name = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade', required=False,
        help="Vendor of this product", check_company=True)
    min_qty = fields.Float(
        'Quantity', default=0.0, required=False, digits="Product Unit Of Measure",
        help="The quantity to purchase from this vendor to benefit from the price, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    price = fields.Float(
        'Price', default=0.0, digits='Product Price',
        required=False, help="The price to purchase a product")
    delay = fields.Integer(
        'Delivery Lead Time', default=1, required=False,
        help="Lead time in days between the confirmation of the purchase order and the receipt of the products in your warehouse. Used by the scheduler for automatic computation of the purchase order planning.")
    vendor_code = fields.Char()
    vendor_name = fields.Char()
    vendor_part = fields.Char()
    vendor_order_multi = fields.Float()
    vendor_cost = fields.Float()
    last_pur_cost = fields.Float()
    last_cost_change = fields.Float()
    last_pur_qty = fields.Float()
    last_pur_date = fields.Date()
    last_po_number = fields.Char()
    discontinued = fields.Char()
    store_closeout = fields.Char()
    desc_line_one = fields.Char()
    desc_line_two = fields.Char()

    @api.onchange('mfg')
    def name_onchange(self):
        for rec in self:
            if rec.mfg:
                rec.name = rec.mfg.vendor

    # @api.model
    # def create(self, vals):
    #     res = super(SupplierInherit, self).create(vals)
    #     if res.product_tmpl_id:
    #         print(res.product_tmpl_id.mfg, res.product_tmpl_id.mfg_vende)


class MfgVendor(models.Model):
    _name = "wg.mfg.vendor"

    name = fields.Char('Name')
    vendor = fields.Many2one('res.partner')
    # vendor_code = fields.Char(related='vendor.vendor')
    company_id = fields.Many2one('res.company', 'Store')
    # sku_id = fields.Many2one('product.template')

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         if rec.name and rec.vendor.name:
    #             print(rec.name, rec.vendor.vendor)
    #             name = rec.name + '-' + rec.vendor.name
    #         else:
    #             name = rec.name
    #         result.append((rec.id, name))
    #     return result

class Stockrecrules(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    department_id = fields.Many2one('hr.department', ondelete='restrict', index=True,string="Dept" )