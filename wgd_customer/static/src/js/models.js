odoo.define('wgd_customer.models', function (require) {
var models = require('point_of_sale.models');
var DB = require('point_of_sale.DB');

// var core = require('web.core');
//var PaymentStripe = require('pos_stripe.payment');


//models.register_payment_method('stripe', PaymentStripe);
models.load_fields('res.partner', 'sort_name_id');
models.load_fields('res.partner', 'customer_id');
models.load_fields('res.partner', 'job_ids');

DB.include({

	        _partner_search_string: function(partner){
	        var str =  partner.name || '';
	        

	        if(partner.barcode){
	            str += '|' + partner.barcode;
	        }
	        if(partner.address){
	            str += '|' + partner.address;
	        }
	        if(partner.phone){
	            str += '|' + partner.phone.split(' ').join('');
	        }
	        if(partner.mobile){
	            str += '|' + partner.mobile.split(' ').join('');
	        }
	        if(partner.email){
	            str += '|' + partner.email;
	        }
	        if(partner.vat){
	            str += '|' + partner.vat;
	        }
	        if(partner.sort_name_id){
	            // console.log("*****222",partner.sort_name_id)

	            str += '|' + partner.sort_name_id;
	        }if(partner.customer_id){
	            // console.log("*****222",partner.sort_name_id)

	            str += '|' + partner.customer_id;
	        }
	        if(partner.job_ids){
	            // console.log("*****222",partner.sort_name_id)

	            str += '|' + partner.job_ids;
	        }
	        str = '' + partner.id + ':' + str.replace(':', '').replace(/\n/g, ' ') + '\n';
	        return str;
	    }
    });

// console.log('00000000008888888888888000000000000000000077777')
});