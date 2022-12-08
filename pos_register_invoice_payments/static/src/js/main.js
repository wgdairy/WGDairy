/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_register_invoice_payments.pos_register_invoice_payments', function(require) {
    "use strict";
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc')
    var QWeb = core.qweb;
    const InvoiceListScreenWidget = require('pos_invoice_details.pos_invoice_details').InvoiceListScreenWidget;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    models.load_models([{
        model:'account.journal',
        field: [],
        domain: function(self){ return [['company_id', '=', self.company.id], ['type', 'in', ['bank', 'cash']]]},
        loaded: function(self, journals){
            self.journals = journals
        }
    }], { 'after': 'pos.config' });

    class RegisterPaymentPopup extends AbstractAwaitablePopup {
        mounted() {
            var self = this;
            super.mounted();
            self.render_invoice_payment_lines(self.props);
            if ($('.tab-link').length) {
                $('.tab-link').removeClass('current');
                if (self.props.payments_widget) {
                    $($('.tab-link')[0]).click();
                } else if (self.props.outstanding_credits) {
                    $($('.tab-link')[1]).click();
                }
            }
            $(".popups").on("click",'.reconsile_line', function(event) {
            self.remove_move_reconcile(event);
            })
            $(".popups").on("click",'.outstanding_credit_line', function(event) {
                self.wk_use_outstanding_credit(event)
            })
        }
        wk_use_outstanding_credit(event){
            var self = this;
            var wk_id = $(event.target).length ? $(event.target)[0].id : false;
            $('.outstanding_credit_line').css('pointer-events', 'none')
            $(event.target).css("background", "#e3f6ed")
            $(event.target).closest('tr').css("background", "#e3f6ed");
            var invoice = self.props.invoice;
            if (wk_id && invoice) {
                rpc.query({
                        model: 'account.move',
                        method: 'wk_assign_outstanding_credit',
                        args: [invoice.id, parseInt(wk_id)],
                    }).then(function(result) {
                        if (result) {
                            var outstanding_credits;
                            var payments_widget;
                            var invoice = self.props.invoice;
                            if (result && result.length && invoice) {
                                invoice.amount_total = result[0].amount_total;
                                invoice.amount_residual = result[0].amount_residual;
                                outstanding_credits = JSON.parse(result[0].invoice_outstanding_credits_debits_widget);
                                payments_widget = JSON.parse(result[0].invoice_payments_widget);
                                invoice.state = result[0].state;
                            }
                            var data = {
                                outstanding_credits: outstanding_credits,
                                payments_widget: payments_widget,
                                invoice: invoice
                            };
                            self.update_residual_amount(invoice.amount_residual);
                            self.render_invoice_payment_lines(data);
                        }
                        $('.outstanding_credit_line').css('pointer-events', '')
                    })
                    .catch(function(error) {
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Failed To Register Payment'),
                            body: self.env._t('Please make sure you are connected to the network.'),
                        });
                        $('.outstanding_credit_line').css('pointer-events', '')
                    });
            }
        }
        wk_rerender_lines(invoice_id) {
            var self = this;
            var invoice_id = parseInt(invoice_id);
            rpc.query({
                    model: 'account.move',
                    method: 'read',
                    args: [
                        [invoice_id],
                    ],
                })
                .then(function(result) {
                    var outstanding_credits;
                    var payments_widget;
                    var invoice = self.props.invoice;
                    if (result && result.length && invoice) {
                        invoice.amount_total = result[0].amount_total;
                        invoice.amount_residual = result[0].amount_residual;
                        outstanding_credits = JSON.parse(result[0].invoice_outstanding_credits_debits_widget);
                        payments_widget = JSON.parse(result[0].invoice_payments_widget);
                        invoice.state = result[0].state;
                    }
                    var data = {
                        outstanding_credits: outstanding_credits,
                        payments_widget: payments_widget,
                        invoice: invoice
                    };
                    self.update_residual_amount(invoice.amount_residual);
                    self.render_invoice_payment_lines(data);
                })
                .catch(function(unused, event) {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Failed To  Rerender Lines'),
                        body: self.env._t('Please make sure you are connected to the network.'),
                    });
                });
        }
        remove_move_reconcile(event){
            var self = this;
            var paymentId = $(event.target).length ? $(event.target)[0].id : false;
            var invoice_id = self.props.invoice ? self.props.invoice.id : false;
            $('.reconsile_line').css('pointer-events', 'none');
            $(event.target).css("background", "#db8b8b")
            $(event.target).closest('tr').css("background", "#db8b8b")
            if (paymentId && invoice_id) {
                rpc.query({
                        model: 'account.move.line',
                        method: 'remove_move_reconcile',
                        args: [parseInt(paymentId)]
                    }).then(function() {
                        self.wk_rerender_lines(invoice_id);
                        $('.reconsile_line').css('pointer-events', '');
                    })
                    .catch(function(unused, event) {
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Failed To  Rerender Lines'),
                            body: self.env._t('Please make sure you are connected to the network.'),
                        });
                        $('.reconsile_line').css('pointer-events', '');
                    });
            }
        }
        render_invoice_payment_lines(data) {
            var self = this;
            var payments_widget_lines = data.payments_widget ? data.payments_widget.content : [];
            var credit_lines = data.outstanding_credits ? data.outstanding_credits.content : [];
            var invoice = data.invoice

            var contents = $('.payment-widget-list-contents');
            contents.innerHTML = "";
            payments_widget_lines.forEach(function(content) {
                var paymentline_html = QWeb.render('WkPaymentWidgetline', {
                    widget: self.env,
                    content: content
                });
                var paymentline = document.createElement('tbody');
                paymentline.innerHTML = paymentline_html;
                paymentline = paymentline.childNodes[1];
                $(contents[0]).empty();
                contents[0].appendChild(paymentline);
            });

            var creditcontents = $('.outstanding-credit-list-contents');
            $(creditcontents).empty();
            creditcontents.innerHTML = "";
            credit_lines.forEach(function(content) {
                var credit_line_html = QWeb.render('WkOutstandingCreditline', {
                    widget: self.env,
                    content: content
                });
                var credit_lines = document.createElement('tbody');
                credit_lines.innerHTML = credit_line_html;
                credit_lines = credit_lines.childNodes[1];
                creditcontents[0].appendChild(credit_lines);
            });

            if (!payments_widget_lines.length) {
                $('.tab-link.reconsile').removeClass('current');
                $('.tab-link.reconsile').hide();
                $('#reconsile_tab').removeClass('current');
                $('.tab-link.outstanding_credits').click();
            } else {
                $('.tab-link.reconsile').show();
            }
            if (!credit_lines.length) {
                $('.tab-link.outstanding_credits').removeClass('current');
                $('.tab-link.outstanding_credits').hide();
                $('#outstanding_credits_tab').removeClass('current');
                $('.tab-link.reconsile').click();
            } else {
                $('.tab-link.outstanding_credits').show();
            }
            if (invoice.amount_residual) {
                $('.tab-link.manual_payment').show();
                if (!(payments_widget_lines.length || credit_lines.length))
                    $('.tab-link.manual_payment').click();
            } else {
                $('.tab-link.manual_payment ').hide();
                $('#register_payment_tab').removeClass('current');
            }
        }
        clickTabChange(event){
            var target_tab_id = $(event.target)[0].id;
            if (target_tab_id) {
                $('.tab-content').removeClass('current');
                $('.tab-link').removeClass('current');
                $(event.currentTarget).addClass('current');
                $(target_tab_id).addClass('current');
                if (target_tab_id == '#register_payment_tab')
                    $('.button.register_payment').show();
                else
                    $('.button.register_payment').hide();
            }
        }
        clickRegisterPayment(event){
            var self = this;
            var cust_id = false
            var invoice = self.props.invoice;
            var amount = parseFloat($('.payment_amount').val());
            var payment_memo = $('.payment_memo').val();
            var wk_payment_journal = parseInt($('.wk_payment_journal').val());

            console.log('=============',invoice.name,wk_payment_journal)

            console.log('=======1111111======',self['partner_id'])
            console.log(payment_memo)
            cust_id = invoice.partner_id
            var wk_register = _.find(self.env.pos.payment_methods, function(method) { return method.id == wk_payment_journal; });

            console.log('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',cust_id[0])
            
            rpc.query({
                model: 'account.journal',
                method: 'get_journal',
                args: [{
                    'journal': wk_payment_journal,
                }]
            })
            .then(function(result){

            console.log("get journal=====",result)
                if (result){
                    var data ={'amount':amount,'partner_id':cust_id[0],'order_no':invoice.name,'inv_type':'invoice_payment','payment_memo': payment_memo,
                                'payment_method_id': wk_payment_journal,
                                'invoice_id': invoice,
                                'journal_id': wk_payment_journal,
                                'pos_order_id':self.env.pos.get_order().id,
                                'session_id': self.env.pos.pos_session.id,
                                'self':self,
                                'is_inv_payment':true}
                    self.showPopup('ConnectPaymentPopUp', {
                            'title': 'John Deere Payment',
                            'vals':data,
                            // 'vals':{},
                            'total_amount':self.env.pos.format_currency(amount),
                            'partner_id':cust_id,
                    });

                }
                else{

                    console.log("Hai all")

                    if (amount <= 0 || !amount) {
                        $('.payment_amount').removeClass('text_shake');
                        $('.payment_amount').focus();
                        $('.payment_amount').addClass('text_shake');
                        return;
                    } else if ($('.wk_payment_journal').val() == "") {
                        $('.wk_payment_journal').removeClass('text_shake');
                        $('.wk_payment_journal').focus();
                        $('.wk_payment_journal').addClass('text_shake');
                        return;
                    } else {
                        $('.button.register_payment').css('pointer-events', 'none')
                        rpc.query({
                                model: 'account.move',
                                method: 'wk_register_invoice_payment',
                                args: [{
                                    'amount': amount,
                                    'payment_memo': payment_memo,
                                    'payment_method_id': wk_payment_journal,
                                    'invoice_id': invoice.id,
                                    'journal_id': wk_payment_journal,
                                    'pos_order_id':self.env.pos.get_order().id,
                                    'session_id': self.env.pos.pos_session.id,
                                }]
                            })
                            .then(function(result) {
                                if (result && result.residual >= 0) {
                                    invoice.amount_residual = parseFloat(result.residual);
                                    if (result.state)
                                        invoice.state = result.state;
                                    
                                    self.cancel();
                                    self.update_residual_amount(invoice.amount_residual);
                                };
                                $('.button.register_payment').css('pointer-events', '')
                            })
                            .catch(function(unused, event) {
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Failed To Register Payment'),
                                    body: self.env._t('Please make sure you are connected to the network.'),
                                });
                                $('.button.register_payment').css('pointer-events', '')
                            });
                    }
                }

            });

            
        }
        update_residual_amount(amount) {
            var self = this;
            var invoice = self.props.invoice;
            $('.wk_residual_amount.text_shake').removeClass('text_shake');
            $('.wk_residual_amount').addClass('text_shake');
            $('.wk_residual_amount').text('Amount Due : ' + self.env.pos.format_currency(amount));
            $('.wk_invoice_state h2').text(invoice.state[0].toUpperCase() + invoice.state.slice(1));
            $('.invoice-line.wk_highlight td:last-child').text(self.env.pos.format_currency(amount));
            $('.selected_line_residual_amount').text(self.env.pos.format_currency(amount));
        }
    }
    RegisterPaymentPopup.template = 'RegisterPaymentPopup';
    Registries.Component.add(RegisterPaymentPopup);

    const PosResInvoiceListScreenWidget = (InvoiceListScreenWidget) =>
    class extends InvoiceListScreenWidget {
        display_invoice_details(visibility, invoice, clickpos) {
            var self = this;
            super.display_invoice_details(visibility, invoice, clickpos);
            $(".wk_register_payment").on("click", function() {
                rpc.query({
                    model: 'account.move',
                    method: 'read',
                    args: [
                        [invoice.id],
                        ['invoice_outstanding_credits_debits_widget', 'invoice_payments_widget', 'state', 'amount_total', 'amount_residual']
                    ],
                })
                .then(function(result) {
                    var outstanding_credits;
                    var payments_widget;
                    if (result && result.length) {
                        invoice.amount_total = result[0].amount_total;
                        invoice.amount_residual = result[0].amount_residual;
                        outstanding_credits = JSON.parse(result[0].invoice_outstanding_credits_debits_widget);
                        payments_widget = JSON.parse(result[0].invoice_payments_widget);
                    }
                    self.showPopup('RegisterPaymentPopup', {
                        outstanding_credits: outstanding_credits,
                        payments_widget: payments_widget,
                        invoice: invoice
                    });
                })
                .catch(function(unused, event) {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Failed To Register Payment'),
                        body: self.env._t('Please make sure you are connected to the network.'),
                    });
                });
                
            });
        }
    };
    Registries.Component.extend(InvoiceListScreenWidget, PosResInvoiceListScreenWidget);
});

// odoo.define('pos_register_invoice_payments.RegisterPaymentPopup', function(require) {
//     'use strict';