from odoo import models, fields, api





class Stockmov(models.Model):
    _inherit = "stock.move"

    pic_id = fields.Many2one('stock.picking',ondelete='restrict', index=True,)
    name = fields.Char('Description', required=False)
    # sku_id = fields.One2many('product.template', 'picking_id',)
    sku_id = fields.Many2one('product.template',  help='Exportable',string="SKU")
    statuss = fields.Selection([('P', 'P'), ('C', 'C'),],string="Status")
    ln = fields.Char(string="Ln#")
    loc  = fields.Char(string="Loc")
    Descriptionss = fields.Char(string="Description")
    QOH  = fields.Float(string="QOH")
    QOO_Pur = fields.Float(string="QOO(Pur)")
    um_pur = fields.Char(string="U/M(Pur)")
    Qty_Being_Recvd = fields.Float(string="Qty Being Recvd(Stk)")
    Variance = fields.Float(string="Variance(Stk)")
    Varaiance_Pur = fields.Float(string="Varaiance(Pur)")
    Qty_Being_Recvd_Pur = fields.Float(string="Qty Being Recvd(Pur)")
    Cost_Pur = fields.Float(string="Cost(Pur)")
    QOO_Ext_Cost = fields.Float(string="QOO Ext Cost")
    Added_in_Receiving = fields.Selection([('yes', 'YES'), ('no', 'NO'),],string="Added in Receiving")
    ERP_d = fields.Selection([('yes', 'YES'), ('no', 'NO'),],string="ERP d")
    ERP_d_Qty = fields.Float(string="ERP d Qty")
    Total_Qty_Received = fields.Float(string="Total Qty Received")
    Total_Qty_Rejected = fields.Float(string="Total Qty Rejected")
    Reject_Reasons = fields.Char(string="Reject Reasons")
    product_id = fields.Many2one(
        'product.product', 'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=False,
        states={'done': [('readonly', True)]})

    date = fields.Datetime(
        'Date Scheduled', default=fields.Datetime.now, index=True, required=False,
        help="Scheduled date until move is done, then date of actual move processing")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True, required=False)
    product_id = fields.Many2one(
        'product.product', 'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=False,
        states={'done': [('readonly', True)]})
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit of Measure',
        default=1.0, required=False, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    product_uom = fields.Many2one('uom.uom', "UoM", required=False,
                                  domain="[('category_id', '=', product_uom_category_id)]")
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=False,
        check_company=True,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=False,
        check_company=True,
        help="Location where the system will stock the finished products.")
    procure_method = fields.Selection([
        ('make_to_stock', 'Default: Take From Stock'),
        ('make_to_order', 'Advanced: Apply Procurement Rules')], string='Supply Method',
        default='make_to_stock', required=False, copy=False,
        help="By default, the system will take from the stock in the source location and passively wait for availability. "
             "The other possibility allows you to directly create a procurement on the source location (and thus ignore "
             "its current stock) to gather products. If we want to chain moves and have this one to wait for the previous, "
             "this second option should be chosen.")
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status',
        copy=False, default='draft', index=True, readonly=False,
        help="* New: When the stock move is created and not yet confirmed.\n"
             "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"
             "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to be manufactured...\n"
             "* Available: When products are reserved, it is set to \'Available\'.\n"
             "* Done: When the shipment is processed, the state is \'Done\'.")



class Stockpick(models.Model):
    _inherit = "stock.picking"

    # movee_ids = fields.One2many('stock.move', 'pic_id', copy=True)
    po = fields.Many2one('purchase.order')
    line = fields.Char(string="Line")
    sku_pur = fields.Many2one('product.template')
    store = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    received_stk = fields.Char(string="Received(Stk)")
    received_pur = fields.Char(string="Received(Pur)")
    cost_stk = fields.Char(string="Cost(Stk)")
    cost_pur = fields.Char(string="Cost(Pur)")
    retail = fields.Char(string="Rentail")
    qoh = fields.Float(string="QOH")
    qoo = fields.Float(string="QOO")
    vendor = fields.Char(string="Vendor")
    descri = fields.Char(string="Description")
    due_date = fields.Date(string="Due Date")
    orig_stk_unit = fields.Float(string="Orig Stk Unit")
    orig_stk_cost = fields.Float(string="Orig Stk Cost", required=True)
    orig_stk_weight = fields.Float(string="Orig Stk Weight")
    BkOrd = fields.Selection([('Y', 'Y'), ('N', 'N'), ],string="BkOrd")
    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',
        default='direct', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="It specifies goods to be deliver partially or all at once")
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    origin = fields.Char(
        'PO #', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    date_deadline = fields.Datetime(
        "Due Date",
        help="Date Promise to the customer on the top level document (SO/PO)",readonly=False)  #compute='_compute_date_deadline', compute field removed and store=True,

    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        check_company=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company', related='picking_type_id.company_id',
        readonly=False, store=True, index=True)





