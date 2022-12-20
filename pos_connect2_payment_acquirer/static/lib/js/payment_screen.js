/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_connect2_payment_acquirer.payment_screen', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var src = window.location.pathname;
    var config_id = src.split('payment/') && src.split('payment/')[1][0];
    var clientSecret = null;
    var card = null;
    var current_transaction = null;
    var is_refresh = true;



    var screenRetrieve;

    function retrieve_screen_updates() {
        ajax.jsonRpc("/pos/payment/"+ config_id +"/update/", 'call', {'template_screen_type':$('.main_body').attr('screen-type'),'is_refresh':is_refresh})
            .then(function (vals) {
                if(vals && ((vals.screen_data && vals.screen_data.length) || (vals.payment_data && vals.payment_data.length))){
                    if(vals.type_of_screen == 'payment'){
                        ajax.loadXML('/pos_connect2_payment_acquirer/static/src/xml/pos_connect.xml', QWeb).then(function (res) {
                        // var data_html = QWeb.render('KitchenDataTemplate', {
                            console.log("res",res);
                            var boyd_html = QWeb.render('connectPaymentTemplate',{
                                'company':vals.company,
                                'payment_amount':vals.payment_amount,
                                'customer_name':vals.customer_name
                            });
                            // boyd_html.replace('payment_url','')
                            $('.main_body').html(boyd_html);
                            is_refresh = false;
                            rpc.query({
                                'method':'update_screen_info',
                                'model':'pos.payment.screen.config',
                                'args':[parseInt(config_id)]
                            })
                            var data_for_element = JSON.parse(vals.payment_data[0].txn_data);
                            current_transaction = vals.payment_data[0].id;
                            var data = setupElements(data_for_element);
                            $('.main_body').attr('screen-type',vals.type_of_screen)
                            clientSecret = data.clientSecret;
                            card = data.card;

                            var form = $('#payment-form');
                            $('#customer-name').focus(function(ev){
                                $('#customer-name').removeClass('wk-error');
                            });
                            $('#customer-phone').focus(function(ev){
                                $('#customer-phone').removeClass('wk-error');
                            });
                        })
                    }
                    else{
                        ajax.loadXML('/pos_connect2_payment_acquirer/static/src/xml/pos_connect.xml', QWeb).then(function (res) {
                            var images = vals.images.map(function(res){
                                return 'data:image/png;base64,'+res.image;
                            })
                            var boyd_html = QWeb.render('PosWelcomeScreenTemplate',{
                                'screen_data':vals.screen_data[0],
                                'images':images,
                                'pos_name':vals.pos_name,
                                'company':vals.company

                            });
                            $('.main_body').html(boyd_html);
                            is_refresh = false;
                            $('.main_body').attr('screen-type',vals.type_of_screen)
                            rpc.query({
                                'method':'update_screen_info',
                                'model':'pos.payment.screen.config',
                                'args':[parseInt(config_id)]
                            })
                            // var data_for_element = JSON.parse(vals.payment_data[0].txn_data);
                            // var data = setupElements(data_for_element);
                            // console.log("Data",data)
                        })
                    }
                }

            });
        // time_calculator_grid();

    }
    screenRetrieve = setInterval(retrieve_screen_updates, 2000);

    function update_transaction_status(is_update,data,transaction_id,config_id,customer_data){
        rpc.query({
            'method': 'update_payment_status',
            'model':'pos.payment.transaction',
            'args':[is_update,data,transaction_id,parseInt(config_id),customer_data]
        }).then(function(){
            retrieve_screen_updates();
        }).catch(function(){
            retrieve_screen_updates();
        });
    }



});
