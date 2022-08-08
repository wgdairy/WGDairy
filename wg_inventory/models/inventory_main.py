from odoo import models, fields, api

class Inventorys(models.Model):
    _inherit = "product.template"

    sku = fields.Char('SKU')
    desc = fields.Char('Desc')
    mfg = fields.Char('Mfg#')
    Desc = fields.Char('Desc')
    upc = fields.Char('UPC')
    dept = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    class_inven = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    prime_ved = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Prime Vend")
    mfg_vend = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Mfg Vend")
    fineline = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Fineline")
    types = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    store = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    sequence = fields.Char('Sequence')
    instore = fields.Char('Instore')
    pursku_ids = fields.Many2one('stock.picking')
    # quantity
    qut_on_hant = fields.Float('Qty On Hant ')
    commited_qty = fields.Float('Commited Qty')
    qty_on_order = fields.Float('Qty On Order')
    custbackorder = fields.Char('Custbackorder')
    location = fields.Char('Location')
    future_order = fields.Char('Future Order')

    # stock level------------------------------
    order_point = fields.Float('Order Point ')
    min_order_ponit = fields.Float('Min Order Ponit')
    max_stock_level = fields.Float('Max Stock Level')
    safety_stock = fields.Float('Safety Stock')
    stockings_UM = fields.Float('Stocking U/M"')
    standard_pack = fields.Float('Standard Pack')
    order_multiple = fields.Float('Order Multiple')

    raincheck_qty = fields.Float('Raincheck Qty')

    # purchasing

    purchasing_um = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Purchasing U/M")
    order_indictor = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="Order Indictor")
    weight = fields.Float('Weight')
    weight_uom = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    # upc = fields.Integer('UPC')
    new_order_qty = fields.Float('New Order Qty')
    purch_conv_factor = fields.Float('*Purch Conv Factor')
    purch_decimal_pi = fields.Float('*Purch Decimal PI')
    min_of_std_pkgs = fields.Char('Min # of Std Pkgs')
    secondary_vend = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    vend_stk = fields.Char('Vend Stk #')
    po_season = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ], string="PO Season")

    # Dates
    date_added = fields.Date(string="Date Added")
    last_sale = fields.Date(string="Last Sale")
    last_receipt = fields.Date(string="Last Receipt")
    last_phy_inv = fields.Date(string="Last Phys Inv")
    catalog_date = fields.Date(string="Catalog Date")
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
    synchronize_price = fields.Float('Synchronize Price')
    synchronize_cost = fields.Float('Synchronize Cost')
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

    jan = fields.Integer()
    feb = fields.Integer()
    mar = fields.Integer()
    apr = fields.Integer()
    may = fields.Integer()
    jun = fields.Integer()
    july = fields.Integer()
    aug = fields.Integer()
    sep = fields.Integer()
    oct = fields.Integer()
    nov = fields.Integer()
    dec = fields.Integer()
    jun_21 = fields.Integer()

    to_date = fields.Integer()
    last_per = fields.Date(string="Last Per")
    # year to date
    transactions = fields.Float()
    sale_units = fields.Float()
    sale = fields.Float()
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
    #doubt in prime vend
    prime_vend_history = fields.Char()
    other_purch = fields.Char()
    kit_sales_unit = fields.Char()
    kit_sale = fields.Char()
    turns = fields.Float()
    his_future_order = fields.Char('Future Order')
    his_order_multiple = fields.Float('Order Multiple')
    his_popularity_code = fields.Selection([('y', 'Y'), ('n', 'N'), ])

    # last year
    last_year_sale_unit = fields.Char()
    last_year_sale = fields.Float()
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


    #note
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
    load_standard_pack = fields.Float()
    load_order_multiple = fields.Float()
    load_purchase_um = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    order_indicator = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    load_weight = fields.Float()
    load_weight_unit = fields.Selection([('LB', 'LB'), ('KG', 'KG'),('Gram', 'Gram') ])
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
    weight_mic_unit = fields.Selection([('LB', 'LB'), ('KG', 'KG'),('Gram', 'Gram') ])
    cubes = fields.Float()
    cubes_unit = fields.Char()
    ebt = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    fsa = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    restricted_houres = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    age_restrict = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    special_fee_code = fields.Selection([('Y', 'Y'), ('N', 'N'), ])
    weighable = fields.Selection([('Y', 'Y'), ('N', 'N'), ])


    # vendor

    vend_ids = fields.One2many('inv_vendor', 'vend_ids', string="Trips and Tolls")



#Table in pricing tab
class Pricetable(models.Model):
    _name = "pricingtables"
    units = fields.Char(string="Units")
    price = fields.Char(string="Pricing")
    stock = fields.Char(string="Stock")
    alt = fields.Char(string="Alt")
    gp = fields.Char(string="GP %")
    blk = fields.Char()
    prc_ids = fields.Many2one('product.template')

#Table for vendor
class inv_vendor(models.Model):
    _name = "inv_vendor"
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
    vend_ids = fields.Many2one('product.template')


