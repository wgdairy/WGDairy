odoo.define('pos_connect.PaymentScreen', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    const PosWechatPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {


            constructor() {
                super(...arguments);
                useListener('refresh-payment-line', this.click_refresh_paymentline);
            }


            click_refresh_paymentline(){
                var self = this;
                // $('.paymentlines-container').unbind().on('click', '.refresh-button', function (event) {
                    var lines = self.env.pos.get_order().get_paymentlines();
                    var selected_paymentline = self.env.pos.get_order().selected_paymentline;
                    var due = 0;
                    for (var i = 0; i < lines.length; i++) {
                        if (lines[i].connect_payment_pending) {
                            due = lines[i].amount;
                            break;
                        }
                    }
                    if(self.env.pos.config.type_of_payment_screen == 'pos'){
                        var txn_amount = selected_paymentline.txn_amount;
                        var due_amount = 0;
                        var payment_amount = 0;
                        if (self.env.pos.currency.name in self.env.pos.db.zero_decimal_currencies){
                            due_amount = due;
                            payment_amount = txn_amount;
                        }
                        else{
                            due_amount = parseFloat(due * 100);
                            payment_amount = parseFloat(txn_amount * 100);
                        }
                        if (Number.isInteger(due_amount)) {
                            console.log("selelctdd aout",due,selected_paymentline.is_connect_payment_failed)
                            if (selected_paymentline && selected_paymentline.is_connect_payment_failed && due_amount == payment_amount) {
                                
                                self.showPopup('ConnectPaymentPopUp', {
                                    'title': 'Connect2 Payment',
                                    'vals':selected_paymentline.pos_txn_data,
                                    'total_amount':self.env.pos.format_currency(selected_paymentline.txn_amount),
                                    'pos_txn_id':selected_paymentline.payment_txn_id
                                });
                            }
                        } else {
                            self.showPopup('ErrorPopup', {
                                'title': _t('Error'),
                                'body': _t('Please Enter Amount In An Integer Value.'),
                            });
                        }
                    }
                    else{
                        rpc.query({
                            'method':'refresh_paymentline',
                            'model':'pos.payment.transaction',
                            'args':[selected_paymentline.payment_txn_id,self.env.pos.db.pos_connect_screen_data.id]
                        }).catch(function(e){
                            self.showPopup('ErrorPopup', {
                                'title': _t('Error'),
                                'body': _t("Please Check The Internet Connection."),
                            });
                        })
                    }

                    $('.paymentline.selected .refresh-button .fa-refresh').addClass('fa-spin')
            //     });
            // }
        }

    // click_paymentmethods (id) {
        addNewPaymentLine({ detail: paymentMethod }) {
            var self = this;
            var current_order = self.env.pos.get_order();
            var due = current_order.get_due();
            if (paymentMethod.connect_payment_method) {
                

                //####################################################################################
                    var existing_line = self.check_existing_connect2_line();
                    var selected_paymentline = null;
                    if (existing_line) {
                        this.showPopup('ErrorPopup', {
                            'title': _t('Error'),
                            'body': _t('One John deere payment scan already pending.'),
                        });
                    } else {
                        // this._super(id);
                    super.addNewPaymentLine({ detail: paymentMethod })
                    selected_paymentline = current_order.selected_paymentline;
                    if (selected_paymentline) {

                        var due_amount = 0;
                        console.log("lllllllllll",due)
                        if (self.env.pos.currency.name in self.env.pos.db.zero_decimal_currencies) {
                            due_amount = due;
                        } else {
                            due_amount = parseFloat(due * 100);
                        }
                        var amount = 0;
                        if (Number.isInteger(due_amount)) {
                            amount = due
                        } else {
                            amount = due
                            due_amount = Math.ceil(due_amount)
                        }
                        selected_paymentline.connect_payment_pending = true;
                        selected_paymentline.is_connect_payment_line = true;
                        var cust_id =false
                        if (self.env.pos.get_order().get_client()){
                            cust_id = self.env.pos.get_order().get_client().id
                        }
                        self.env.pos.get_order().selected_paymentline.set_amount(amount)
                        // self.render_paymentlines();
                        if (Number.isInteger(amount))
                            $('.paymentline.selected .edit').text(self.env.pos.format_currency_no_symbol(amount));
                        
                        $('.next').removeClass('highlight');
                        // data ={'publishableKey': '', 'clientSecret': 'intent.client_secret','txn_id':intent.id}
                        var data ={'amount':amount,'partner_id':cust_id,'order_no':self.env.pos.get_order().name,'inv_payment':false}


                        self.showPopup('ConnectPaymentPopUp', {
                            'title': 'John Deere Payment',
                            'vals':data,
                            // 'vals':{},
                            'total_amount':self.env.pos.format_currency(amount),
                            'partner_id':cust_id,
                        });
            }
            } 
            }
            else {
                super.addNewPaymentLine({ detail: paymentMethod })
                // this._super(id);
            }

        }


        check_existing_connect2_line () {
            var self = this;
            var current_order = self.env.pos.get_order();
            var existing_connect2_line = null;
            var paymentlines = current_order.get_paymentlines();
            if (self.env.pos.db.connect_payment_method) {
                paymentlines.forEach(function (line) {
                    if (line.payment_method.id == self.env.pos.db.connect_payment_method.id && line.connect_payment_pending) {
                        line.is_connect_payment_line = true;
                        existing_connect2_line = line;
                        return true;
                    }
                });
            }
            return existing_connect2_line;
        }

        create_payment_transaction(data,order_ref,amount,config_id,created_from,state){
            var self = this;
            var client_id = null;
            if(self.env.pos.get_order() && self.env.pos.get_order().get_client())
                client_id = self.env.pos.get_order().get_client().id;
            if(self.env.pos.db.pos_connect_screen_data)
                rpc.query({
                    'method':'create_payment_transaction',
                    'model':'pos.payment.transaction',
                    'args':[data,order_ref,amount,self.env.pos.db.pos_connect_screen_data.id,config_id,created_from,self.env.pos.format_currency(amount),client_id,state]
                }).then(function(res){
                    self.env.pos.get_order().selected_paymentline.payment_txn_id = res;
                }).catch(function(error){
                    console.log("res************",error)
                })
        }


    
            /**
             * @override
             */
            deletePaymentLine(event) {
            var self = this;
            var lines = this.env.pos.get_order().get_paymentlines();
            for ( var i = 0; i < lines.length; i++ ) {
                var line = lines[i];
                if (line.is_connect_payment_line && line.connect_payment_pending) {
                    // clearInterval(line.interval)
                    line.interval = null;
                    // rpc.query({
                    //     'method': 'update_payment_status',
                    //     'model':'pos.payment.transaction',
                    //     'args':[false,{'message':'Payment Has Been Cancelled!'},line.payment_txn_id,self.env.pos.db.pos_connect_screen_data.id,false]
                    // });
                }
            }
            super.deletePaymentLine(event);
        }







        };

    Registries.Component.extend(PaymentScreen, PosWechatPaymentScreen);

    return PaymentScreen;
});
