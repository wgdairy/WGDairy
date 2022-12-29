

odoo.define('wg_inventory.pos_product_view', function (require) {
var models = require('point_of_sale.models');
var productItem = require('point_of_sale.ProductItem')
//alert('hello world')
//var PaymentStripe = require('pos_stripe.payment');
//models.('',productItem)
//models.register_payment_method('stripe', PaymentStripe);
models.load_fields('product.product', 'sku');
});