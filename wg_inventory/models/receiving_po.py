from odoo import models, fields, api


class Stockmov(models.Model):
    _inherit = "stock.move"

    pic_id = fields.Many2one('stock.picking', ondelete='restrict', index=True, )
    name = fields.Char('Description', required=False)
    # sku_id = fields.One2many('product.template', 'picking_id',)
    sku_id = fields.Many2one('product.template', help='Exportable', string="SKU")
    statuss = fields.Selection([('P', 'P'), ('C', 'C'), ], string="Status")
    ln = fields.Char(string="Ln#")
    # ln = fields.Integer(compute='_get_line_number', string='Ln#', readonly=False, default=False)
    loc = fields.Char(string="Loc")
    Descriptionss = fields.Char(string="Description")
    QOH = fields.Float(string="QOH", related='product_id.qty_available')
    QOO_Pur = fields.Float(string="QOO(Pur)")
    um_pur = fields.Char(string="U/M(Pur)")
    Qty_Being_Recvd = fields.Float(string="Qty Being Recvd(Stk)")
    Variance = fields.Float(string="Variance(Stk)", compute='_cal_variance')
    Varaiance_Pur = fields.Float(string="Varaiance(Pur)")
    Qty_Being_Recvd_Pur = fields.Float(string="Qty Being Recvd(Pur)")
    Cost_Pur = fields.Float(string="Cost(Pur)",compute='_cal_cost_po_line',readonly=False,)
    QOO_Ext_Cost = fields.Float(string="QOO Ext Cost", compute='_cal_cost')
    Added_in_Receiving = fields.Selection([('yes', 'YES'), ('no', 'NO'), ], string="Added in Receiving")
    ERP_d = fields.Selection([('yes', 'YES'), ('no', 'NO'), ], string="ERP d")
    ERP_d_Qty = fields.Float(string="ERP d Qty")
    Total_Qty_Received = fields.Float(string="Total Qty Received")
    Total_Qty_Rejected = fields.Float(string="Total Qty Rejected")
    Reject_Reasons = fields.Char(string="Reject Reasons")

    @api.onchange('quantity_done')
    def onchange_qty_recieved(self):
        '''
        Function to Auto populate the Total Qty Received.
        '''
        if self.quantity_done:
            self.Total_Qty_Received = self.quantity_done

    @api.onchange('product_id')
    def _onchange_sku(self):
        '''
        Function to Auto populate the Description.
        '''
        onc_sku = self.env['product.template'].search(
            [('name', '=', self.product_id.name), ('id', '=', self.product_id.product_tmpl_id.id)])

        self.description_picking = onc_sku.desc


    @api.onchange('product_id')
    def _cal_cost_po_line(self):
        '''
        Function to Auto populate the Cost,Get Cost form product
        '''
        onc_cost = self.env['purchase.order.line'].search([('order_id.name', '=', self.picking_id.origin)])
        for r in onc_cost:
            for i in self:
                if r.product_id == i.product_id:
                    i.Cost_Pur = r.cost_stk

    @api.depends('Cost_Pur', 'product_uom_qty')
    def _cal_cost(self):
        '''
        Function to compute the QOO ext cost
        '''
        for rec in self:
            rec.QOO_Ext_Cost = rec.product_uom_qty * rec.Cost_Pur

    @api.depends('QOO_Pur','quantity_done')
    def _cal_variance(self):
        '''
        Function to compute the Variance
        '''
        for recs in self:
            recs.Variance = recs.product_uom_qty - recs.quantity_done

    @api.onchange('product_id')
    def _cal_qoh(self):
        '''
        Function to Auto populate the Cost QOH, Get QOH form product
        '''
        onc_sku = self.env['product.template'].search([('name', '=', self.product_id.name), ('id', '=', self.product_id.product_tmpl_id.id)])
        self.QOH = onc_sku.qty_available


class Stockpick(models.Model):
    _inherit = "stock.picking"

    # movee_ids = fields.One2many('stock.move', 'pic_id', copy=True)
    po = fields.Many2one('purchase.order')
    line = fields.Char(string="Line")
    sku_pur = fields.Many2one('product.template')
    store = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2'), ])
    store_id = fields.Many2one('res.company', ondelete='restrict', index=True, )
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
    orig_stk_cost = fields.Float(string="Orig Stk Cost")
    orig_stk_weight = fields.Float(string="Orig Stk Weight")
    # BkOrd = fields.Selection([('Y', 'Y'), ('N', 'N'), ],string="BkOrd", compute='_backord')
    BkOrd = fields.Char(string='BkOrd', compute='_backord')


    def _backord(self):
        '''
        If any Back order Set Back order field to Y, if no back orders,Set Back order field to N.
        '''
        for rec in self:
            bak = self.env['purchase.order'].search([('name', '=', rec.origin)],limit=1)
            # for r in bak:

            rec.BkOrd = bak.BkOrds












