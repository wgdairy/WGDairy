/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_connect2_payment_acquirer.pos_connect2_payment_acquirer', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var DB = require('point_of_sale.DB');
    var ProductScreen = require('point_of_sale.ProductScreen');
    var model_list = models.PosModel.prototype.models;
    var SuperPaymentline = models.Paymentline.prototype;
    const Registries = require('point_of_sale.Registries');
    var payment_method_model = null;


	models.load_models([{
		model: 'pos.payment.screen.config',
		label: 'Pos Connect Payment Screen',
		fields: ['related_id','url','welcome_screen_content','welcome_screen_subheading','welcome_screen_heading'],
		loaded: function(self, result) {
          self.db.pos_connect_screen_data = null;
          console.log("result",result)
		  _.each(result, function(data) {
              console.log("data",data,self.config)
			  if(data && (data.related_id[0] == self.config.id)){
                  console.log("Data",data)
                  self.db.pos_connect_screen_data = data;
              }
		  });
		}
	  }],{'after':'pos.config'});

    

    // models.load_fields('pos_connect2.configuration', 'john_deere_financial_legal_invoice_disclosure');

	models.load_models([{
		model: 'promotion.image',
		label: 'Promotional Images',
		fields: ['promotions_related_id','image'],
		loaded: function(self, result) {
		  self.db.connect_screen_promotional_images = [];
		  _.each(result, function(data) {
			  if(data.promotions_related_id[0] == self.db.pos_connect_screen_data.id)
			  	self.db.connect_screen_promotional_images.push(data);
		  });
		}
	  }],{'after':'pos.screen.config'});


    models.load_fields('pos.payment.method', 'connect_payment_method');

    //--Fetching model dictionary--
    for (var i = 0, len = model_list.length; i < len; i++) {
        if (model_list[i].model == "pos.payment.method") {
            payment_method_model = model_list[i];
            break;
        }
    }

    // models.load_models([{
    //     model: 'pos_connect.configuration',
    //     label: 'Connect',
    //     fields: ['name','secret_key', 'publishable_key', 'active_record'],
    //     loaded: function (self, result) {
    //         _.each(result, function (res) {
    //             if (res.active_record) {
    //                 // self.db.stripeApiKey = res;
    //             }
    //         });
    //     }
    // }]);

    //--Searching wallet journal--
    var super_payment_method_loaded = payment_method_model.loaded;
    payment_method_model.loaded = function (self, payment_methods) {
        super_payment_method_loaded.call(this, self, payment_methods);
        payment_methods.forEach(function (payment_method) {
            if (payment_method.connect_payment_method) {
                self.db.connect_payment_method = payment_method;
                return true;
            }
        });
    };

    DB.include({

        init: function (options) {
            this._super(options);
            this.zero_decimal_currencies = {
                'MGA': 'MGA',
                'BIF': 'BIF',
                'PYG': 'PYG',
                'CLP': 'CLP',
                'DJF': 'DJF',
                'RWF': 'RWF',
                'GNF': 'GNF',
                'UGX': 'UGX',
                'VND': 'VND',
                'JPY': 'JPY',
                'VUV': 'VUV',
                'XAF': 'XAF',
                'XOF': 'XOF',
                'XPF': 'XPF',
                'KMF': 'KMF',
                'KRW': 'KRW'
            }

        }
    });




    models.PosModel = models.PosModel.extend({

        setupElements : function(data) {
          // var stripe = Stripe('pk_test_51BTUDGJAJfZb9HEBwDg86TN1KNprHjkfipXmEDMb0gSCassK5T3ZfxsAbcgKVmAIXF7oZ6ItlZZbXO6idTHE67IM007EwQ4uN3');
          // var elements = stripe.elements();
          console.log('elements11111111',elements)
          var style = {
            base: {
              color: '#32325d',
              fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
              fontSmoothing: 'antialiased',
              fontSize: '24px',
              '::placeholder': {
                color: '#aab7c4'
              }
            },
            invalid: {
              color: '#fa755a',
              iconColor: '#fa755a'
            }
          };

          // var card = elements.create("card", { style: style });
          // card.mount("#card-element");
          // card.addEventListener('change', ({error}) => {
          //   const displayError = document.getElementById('card-errors');
          //   if (error) {
          //     displayError.textContent = error.message;
          //   } else {
          //     displayError.textContent = '';
          //   }
          // });

          return {
            // stripe: stripe,
            // card: card,
            clientSecret: data.clientSecret
          };
        },
    })


    var _paylineproto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function (attributes, options) {
            this.is_connect_payment_line = false;
            this.is_connect_payment_failed = false;
            this.is_connect_payment_cancel = false;
            this.last_payment_source = null;
            this.connect_payment_pending = false;
            this.src_id = '';
            SuperPaymentline.initialize.call(this, attributes, options);
        },
        init_from_JSON: function (json) {
            _paylineproto.init_from_JSON.apply(this, arguments);
            this.is_connect_payment_line = json.is_connect_payment_line;
            this.connect_payment_pending = json.connect_payment_pending;
            this.src_id = json.src_id;
        },
        export_as_JSON: function () {
            var self = this;
            var src_id = null;
            if(self.src_id)
                var src_id = self.src_id;
            return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {
                paid: this.paid,
                connect_payment_pending: this.connect_payment_pending,
                is_connect_payment_line: this.is_connect_payment_line,
                src_id:src_id,
            });
        },
    });

    
    var PosResProductScreen = ProductScreen =>
    class extends ProductScreen {
        mounted(){
            var self = this;
            if(self.env.pos.db.pos_connect_screen_data){
                console.log("Start work")
                rpc.query({
                    'method':'update_screen_on_pos',
                    'model':'pos.payment.screen.config',
                    'args':[self.env.pos.db.pos_connect_screen_data.id]
                })
            }
            super.mounted();

        }
    }

    Registries.Component.extend(ProductScreen, PosResProductScreen);

    Registries.Component.freeze();


});
