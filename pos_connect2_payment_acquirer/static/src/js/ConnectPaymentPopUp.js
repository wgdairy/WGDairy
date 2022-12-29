odoo.define('pos_connect.ConnectPaymentPopUp', function(require) {
    'use strict';
    const { useState } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;
    var models = require('point_of_sale.models');

    models.load_models([{
        model: 'pos_connect2.configuration',
        label: 'Pos Connect2 Payment Screen',
        fields: ['terminal_number','credit_plan_number','descriptive_billing_code','john_deere_financial_legal_invoice_disclosure'],
        loaded: function (self, result) {
            _.each(result, function (res) {
                // if (res.active_record) {
                    self.db.john_deere = res;
                // }
            });
        }
      }]);

    class ConnectPaymentPopUp extends AbstractAwaitablePopup {
        mounted () {
            // this._super(options);
            super.mounted();

            console.log("================= get session =====================",this)

            var self = this;
            var vals = self.props.vals;
            var is_cus_invoice = false
            var existing_card_number = ''
            var order_no = vals['order_no']
            var partner_id =false
            var amount = vals['amount']
            var form = $('#payment-form');
            var inv_payment = false
            var order_line =[]

            

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                        'model': 'pos.dbc.code',
                        'method': 'add_dbc_code',
                        'args': [{
                            // 'partner_id':vals['partner_id']
                        }],
                        'kwargs': {
                            'context': {
                            },
                        }
                        
            }).then(function (data) {
                // console.log(data)
                if (data.length>0)
                {   
                    var code = document.getElementById("dbc_code_selection_id");
                    for (var cd = 0; cd < data.length; cd++){
                        var option = document.createElement("option");
                        option.text = data[cd];
                        code.add(option);
                    }
                    

                      
                }
            });

            var mod = self.env.pos.get_order().orderlines.models
            for (var i = 0; i < mod.length; i++)
                order_line[i]={'product':mod[i].full_product_name,'uom':mod[i].product.uom_id,'quantity':mod[i].quantity,'price':mod[i].price}
            
            // show saved card details

            if (vals['partner_id']){
                partner_id = vals['partner_id']
                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                        'model': 'pos.connect.two',
                        'method': 'get_partner_card',
                        'args': [{
                            'partner_id':vals['partner_id']
                        }],
                        'kwargs': {
                            'context': {
                            },
                        }
                    }).then(function (data) {

                        // this.existing_card_number data
                        
                        if (data){
                            var name = ''
                            var card = ''
                            if (data['card_number']){
                                card = data['card_number']
                            }
                            if (data['name'])
                            {
                                name =data['name']
                            }
                            document.getElementById("customer_card_number").value = card;   
                            document.getElementById("customer-name").value = name;   
                        }
                        
                });
            }
            

            form.on('submit',function(ev){

                ev.preventDefault();


                // 'submit clicked check now'
                var customer_name = $('#customer-name').val();
                var card_number = $('#customer_card_number').val();
                var cardno = /^(?:5[1-5][0-9]{10})$/;

                if (card_number == "" || card_number.match(cardno) || card_number.length !=10) {
                    alert("Enter Valid Card Number");
                    return false;
                }
                


            if ('is_inv_payment' in vals){
                    var inv_payment = vals['is_inv_payment']
            }

            
            

            var check_box = document.querySelector('#accept').checked;


            form.css('display','none');
            $('.footer').css('display','none');
            $('.loader-holder').css('display','flex');


            // Purchase or credit api call / data transfer

            var code = document.getElementById("dbc_code_selection_id").value;

            self.props.dbc_code=code;



            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                'model': 'pos.connect.two',
                'method': 'api_call_for_data_transfer',
                'args': [{
                        'customer_name':customer_name,
                        'card-element':card_number,
                        'invoice_amount':amount,
                        'check':check_box,
                        'partner_id':vals['partner_id'],
                        'order_no':order_no,
                        'order_line':order_line,
                        'inv_payment':inv_payment,
                        'dbc_code':code,
                        'config_id':self.env.pos.config_id
                        
                    }],
                'kwargs': {
                    'context': {
                    },
                }
            }).then(function (data) {

                    if (data == "Success" || data.includes("Review")){

                        //To review card details with authorization number

                                if (data.includes("Review"))
                                {

                                    var data_val={'customer_name':partner_id,'card_number':card_number,'inv_amount':amount,'order_no':order_no,'inv_payment':inv_payment,'dbc_code':code}
                                    self.showPopup('connectPurchaseReviewPopUp', {
                                        'title': 'Review Call',
                                        'vals':data_val,
                                        'review_msg':data
                                    });
                                    ev.preventDefault();
                                
                                }
                                else{

                                $('.wk-payment-loader').hide();
                                $('.payment_amount').text('Payment has been completed!!')


                                $('.payment_done').show();
                                $('.payment_order_status').show();
                                $('#payment_order_sent_status').hide();
                                $('.payment_order_status').removeClass('payment_order_done');
                                $('.payment_show_tick').hide();
                                setTimeout(function () {
                                    $('.payment_order_status').addClass('payment_order_done');
                                    $('.payment_show_tick').show();
                                    $('#payment_order_sent_status').show();
                                    $('.payment_order_status').css({
                                        'border-color': '#5cb85c'
                                    })
                                }, 500);
                                setTimeout(function () {
                                    self.cancel();
                                }, 2500);
                                $('.pos .paymentline.selected.o_pos_connect_scan_pending .col-tendered.edit ').removeClass('o_pos_connect_scan_tendered');
                                $('.pos .paymentline.selected').removeClass('o_pos_connect_scan_pending');
                                $('div.payment-screen.screen span.button.next').addClass('highlight');
                                $('.pos .paymentline.selected .delete-button').hide();
                                $('.pos .paymentline.selected .col-name').text('John Deere');
                                $('.refresh-button').hide();
                            }
                                
                            }
                            else{

                                setTimeout(function () {
                                    self.showPopup('PaymentConnectNotifyPopupWidget', {
                                        failed:true,
                                        body:'Payment Failed'
                                    });
                                }, 3500);
                                
                            }
                            if (inv_payment && data.includes("Review")==false && data =="Success")
                            {
                                // data from the sales invoice - payments

                                if (inv_payment && data.includes("Review")==false){

                                 console.log('this is invoice payment===========',vals);

                                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                                'model': 'account.move',
                                'method': 'wk_register_invoice_payment',
                                'args': [{
                                            'amount': vals['amount'],
                                            'payment_memo': vals['payment_memo'],
                                            'payment_method_id': vals['wk_payment_journal'],
                                            'invoice_id': vals['invoice_id'].id,
                                            'journal_id': vals['journal_id'],
                                            'pos_order_id':vals['pos_order_id'],
                                            'session_id': vals['session_id']
                                            }],
                                'kwargs': {
                                    'context': {

                                    },
                                }
                            }).then(function (result) {
                            
                                    if (result && result.residual >= 0) {
                                        vals['invoice_id'].amount_residual = parseFloat(result.residual);
                                        if (result.state)
                                            vals['invoice_id'].state = result.state;
                                        
                                        // vals['self'].cancel();
                                        vals['self'].update_residual_amount(vals['invoice_id'].amount_residual);
                                    };
                                    $('.button.register_payment').css('pointer-events', '')

                            });
                            }
                            }
                            else if (data == "Success"){
                                    if (data.includes("Review")==false && data != "Declined") {
                                        self.env.pos.get_order().selected_paymentline.connect_payment_pending = false;
                                   }
                                
                            }

                                



                    });



                });
        }

        cancel () {
            super.cancel();
            var self = this;
            var interval = this.interval;
            clearInterval(interval);
            $('.paymentline.selected .refresh-button .fa-refresh').removeClass('fa-spin')
            rpc.query({
                'method':'cancel_popup_payment',
                'model':'pos.payment.transaction',
                'args':[self.props.pos_txn_id]
            }).catch(function(e){
                self.showPopup('ErrorPopup', {
                    'title': _t('Error'),
                    'body': _t("Please Check The Internet Connection."),
                });
            })

        }




    }
    ConnectPaymentPopUp.template = 'ConnectPaymentPopUp';
    ConnectPaymentPopUp.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Online Payment',
        body: '',
    };

    Registries.Component.add(ConnectPaymentPopUp);

    return ConnectPaymentPopUp;

});



odoo.define('pos_connect.connectPurchaseReviewPopUp', function(require) {
    'use strict';
    const { useState } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;

    class connectPurchaseReviewPopUp extends AbstractAwaitablePopup {
        mounted () {

            super.mounted();
            var self = this;
            var vals = self.props.vals;
            var form = $('#purchase-review-form');
            var order_no = vals['order_no']

            var order_line =[]




            var mod = self.env.pos.get_order().orderlines.models
            for (var i = 0; i < mod.length; i++)
                // var mo = mod[i]
                order_line[i]={'product':mod[i].full_product_name,'uom':mod[i].product.uom_id,'quantity':mod[i].quantity,'price':mod[i].price}



            // review form with authorization number

            
            form.on('submit',function(ev){
                ev.preventDefault();

                form.css('display','none');
                $('.footer').css('display','none');
                $('.loader-holder-review').css('display','flex');

                var token = $('#authorization_no').val();
                var customer_name = vals['customer_name'];
                var card_number = vals['card_number'];
                var inv_amount = vals['inv_amount'];



                // review the card details with authorization number

                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                    'model': 'pos.connect.two',
                    'method': 'api_call_for_review_data',
                    'args': [{
                            'token_no':1,
                            'customer_name':customer_name,
                            'card_number':card_number,
                            'inv_amount':inv_amount,
                            'order_no':order_no,
                            'inv_payment':vals['inv_payment'],
                            'order_line':order_line,
                            'dbc_code':vals['dbc_code'],
                            'config_id':this.env.pos.config_id
                            
                        }],
                    'kwargs': {
                        'context': {
                        },
                    }
                }).then(function (data) {
                     console.log(data)
                    if (data =="Success")
                    {

                        if(vals['inv_payment'])
                        {
                            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                                'model': 'account.move',
                                'method': 'wk_register_invoice_payment',
                                'args': [{
                                            'amount': vals['amount'],
                                            'payment_memo': vals['payment_memo'],
                                            'payment_method_id': vals['wk_payment_journal'],
                                            'invoice_id': vals['invoice_id'].id,
                                            'journal_id': vals['journal_id'],
                                            'pos_order_id':vals['pos_order_id'],
                                            'session_id': vals['session_id']
                                            }],
                                'kwargs': {
                                    'context': {

                                    },
                                }
                            }).then(function (result) {

                            
                                    if (result && result.residual >= 0) {
                                        vals['invoice_id'].amount_residual = parseFloat(result.residual);
                                        if (result.state)
                                            vals['invoice_id'].state = result.state;
                                        vals['self'].update_residual_amount(vals['invoice_id'].amount_residual);
                                    };
                                    $('.button.register_payment').css('pointer-events', '')

                            });
                        }
                        else
                        {
                            $('.payment_order_status').show();
                            $('.payment_done').show();
                            $('.payment_order_status').show();
                            $('#payment_order_sent_status').hide();
                            $('.payment_order_status').removeClass('payment_order_done');
                            $('.payment_show_tick').hide();
                            setTimeout(function () {
                                $('.payment_order_status').addClass('payment_order_done');
                                $('.payment_show_tick').show();
                                $('#payment_order_sent_status').show();
                                $('.payment_order_status').css({
                                    'border-color': '#5cb85c'
                                })
                            }, 500);
                            setTimeout(function () {
                                self.cancel();
                            }, 2500);
                            $('.pos .paymentline.selected.o_pos_connect_scan_pending .col-tendered.edit ').removeClass('o_pos_connect_scan_tendered');
                            $('.pos .paymentline.selected').removeClass('o_pos_connect_scan_pending');
                            $('div.payment-screen.screen span.button.next').addClass('highlight');
                            $('.pos .paymentline.selected .delete-button').hide();
                            $('.pos .paymentline.selected .col-name').text('John Deere');
                            $('.refresh-button').hide();


                            self.env.pos.get_order().selected_paymentline.connect_payment_pending = false;
                        }
                        
                    

                        

                    }
                    else{

                        setTimeout(function () {
                            self.showPopup('PaymentConnectNotifyPopupWidget', {
                                failed:true,
                                body:'Payment Failed'
                            });
                        }, 3500);
                        
                    }
                
                });

            });
        }
    }
    connectPurchaseReviewPopUp.template = 'connectPurchaseReviewPopUp';
    connectPurchaseReviewPopUp.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Online Payment',
        body: '',
    };
    Registries.Component.add(connectPurchaseReviewPopUp);
    return connectPurchaseReviewPopUp;

});

odoo.define('point_of_sale.models_inherited', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var ajax = require('web.ajax');
    // var legal_disclosure=null
    var rpc = require('web.rpc');
    var session = require('web.session');
    var disclosure = null

    

    models.Order = models.Order.extend({



    export_for_printing: function(){



        var orderlines = [];
        var self = this;
        var john_deere =self.pos.db;


        this.orderlines.each(function(orderline){
            orderlines.push(orderline.export_for_printing());
        });

        // If order is locked (paid), the 'change' is saved as negative payment,
        // and is flagged with is_change = true. A receipt that is printed first
        // time doesn't show this negative payment so we filter it out.
        var paymentlines = this.paymentlines.models
            .filter(function (paymentline) {
                return !paymentline.is_change;
            })
            .map(function (paymentline) {
                return paymentline.export_for_printing();
            });
        var client  = this.get('client');
        var cashier = this.pos.get_cashier();
        var company = this.pos.company;
        var date    = new Date();

        function is_html(subreceipt){
            return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
        }

        function render_html(subreceipt){
            if (!is_html(subreceipt)) {
                return subreceipt;
            } else {
                subreceipt = subreceipt.split('\n').slice(1).join('\n');
                var qweb = new QWeb2.Engine();
                    qweb.debug = config.isDebug();
                    qweb.default_dict = _.clone(QWeb.default_dict);
                    qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');

                return qweb.render('subreceipt',{'pos':self.pos,'order':self, 'receipt': receipt}) ;
            }
        }
        var receipt = {
            orderlines: orderlines,
            paymentlines: paymentlines,
            subtotal: this.get_subtotal(),
            total_with_tax: this.get_total_with_tax(),
            total_rounded: this.get_total_with_tax() + this.get_rounding_applied(),
            total_without_tax: this.get_total_without_tax(),
            total_tax: this.get_total_tax(),
            total_paid: this.get_total_paid(),
            legal_disclosure : john_deere.john_deere.john_deere_financial_legal_invoice_disclosure,
            cpn_no:john_deere.john_deere.credit_plan_number,
            dbc_code:john_deere.john_deere.descriptive_billing_code,
            total_discount: this.get_total_discount(),
            rounding_applied: this.get_rounding_applied(),
            tax_details: this.get_tax_details(),
            change: this.locked ? this.amount_return : this.get_change(),
            name : this.get_name(),
            client: client ? client : null ,
            invoice_id: null,   //TODO
            cashier: cashier ? cashier.name : null,
            precision: {
                price: 2,
                money: 2,
                quantity: 3,
            },
            date: {
                year: date.getFullYear(),
                month: date.getMonth(),
                date: date.getDate(),       // day of the month
                day: date.getDay(),         // day of the week
                hour: date.getHours(),
                minute: date.getMinutes() ,
                isostring: date.toISOString(),
                localestring: this.formatted_validation_date,
                validation_date: this.validation_date,
            },
            company:{
                email: company.email,
                website: company.website,
                company_registry: company.company_registry,
                contact_address: company.partner_id[1],
                vat: company.vat,
                vat_label: company.country && company.country.vat_label,
                name: company.name,
                phone: company.phone,
                logo:  this.pos.company_logo_base64,
            },
            currency: this.pos.currency,
            
        };

        

        if (is_html(this.pos.config.receipt_header)){
            receipt.header = '';
            receipt.header_html = render_html(this.pos.config.receipt_header);
        } else {
            receipt.header = this.pos.config.receipt_header || '';
        }

        if (is_html(this.pos.config.receipt_footer)){
            receipt.footer = '';
            receipt.footer_html = render_html(this.pos.config.receipt_footer);
        } else {
            receipt.footer = this.pos.config.receipt_footer || '';
        }

        return receipt;
    },

   
    
    

});


});


