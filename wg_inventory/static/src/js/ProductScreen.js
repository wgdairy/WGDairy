odoo.define('wg_inventory.pos_product_screen', function (require) {
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session')
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    var productItem = require('point_of_sale.ProductItem')
    var models = require('point_of_sale.models');
    const rpc = require('web.rpc');
    
    // Extending default 'ProductScreen' class in POS 
    const WGProductScreen = ProductScreen => class extends ProductScreen {
            
            // modified '_clickProduct' function 
            async _clickProduct(event) {
            if (!this.currentOrder) {
                this.env.pos.add_new_order();
            }

            // condition to check the customer is selected
            if (!this.currentOrder.get_client()){
                    const product = event.detail;
                    const options = await this._getAddProductOptions(product);
                    if (product.taxes_id){
                        product.taxes_id = []
                    }
                    // Do not add product if options is undefined.
                    if (!options) return;
                    // Add the product after having the extra information.
                    this.currentOrder.add_product(product, options);
                    NumberBuffer.reset();
            }
            else{
                var pos_session = this.env.pos.config_id
                var customer = this.currentOrder.get_client() //getting the customer
                var store_tax = 0
                                        
                const product = event.detail;
                const options = await this._getAddProductOptions(product);

                // calling 'store_tax' function from python : returns list with tax id related store 
                // if customer is taxable else empty list([])
                await rpc.query({
                    method:'store_tax',
                    model: 'product.template',
                    args: [pos_session,customer.id]}).then(function (result) { 
                        store_tax = result[0]
                        if(product.taxes_id){
                            product.taxes_id = [result[0]]
                            // })
                        }
                            
                        return store_tax

                    });
                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                this.currentOrder.add_product(product, options);
                NumberBuffer.reset();
            }
        }
    }
    
    Registries.Component.extend(ProductScreen, WGProductScreen);
    
    return ProductScreen;
    
    
    });