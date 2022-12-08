/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_invoice_details.pos_invoice_details', function(require) {
    "use strict";
    var pos_model = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
    var SuperPosModel = pos_model.PosModel.prototype;
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ClientLine = require('point_of_sale.ClientLine');
	const { useListener } = require('web.custom_hooks');


    pos_model.PosModel = pos_model.PosModel.extend({
        _save_to_server: function(orders, options) {
            var self = this;
            // POS Invoice Details - Dictionary and Loist Update--START--
            return SuperPosModel._save_to_server.call(this, orders, options).then(function(return_dict) {
                _.forEach(return_dict, function(dict){
                    if (dict.invoices != null) {
                        dict.invoices.forEach(function(invoice) {
                            self.db.pos_all_invoices.unshift(invoice);
                            self.db.invoice_by_id[invoice.id] = invoice;
                        });
                        dict.invoice_lines.forEach(function(invoice_line) {
                            self.db.pos_all_invoice_lines.unshift(invoice_line);
                            self.db.invoice_line_by_id[invoice_line.id] = invoice_line;
                        });
                    }
                    delete dict["invoices"];
                    delete dict["invoice_lines"];
                });
                // POS Invoice Details - Dictionary and Loist Update--STOP--
                return return_dict;
            });
        }
    });

    pos_model.load_models([{
        model: 'account.move',
        fields: ['invoice_user_id', 'id', 'name', 'state', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'invoice_line_ids'],
        domain: function(self) {
            return [
                ['state', '!=', 'draft'],
                ['move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund', 'out_receipt', 'in_receipt']]
            ]
        },
        loaded: function(self, invoices) {
            self.db.pos_all_invoices = invoices;
            self.db.invoice_by_id = [];
            invoices.forEach(function(invoice) {
                self.db.invoice_by_id[invoice.id] = invoice;
            });
        }
    }, {
        model: 'account.move.line',
        fields: ['id', 'product_id', 'name', 'account_id', 'quantity', 'price_unit', 'tax_ids', 'price_subtotal'],
        loaded: function(self, invoice_lines) {
            self.db.pos_all_invoice_lines = invoice_lines;
            self.db.invoice_line_by_id = [];
            invoice_lines.forEach(function(invoice_line) {
                self.db.invoice_line_by_id[invoice_line.id] = invoice_line;
            });
        }
    }]);



    const PosResClientLine = (ClientLine) =>
        class extends ClientLine{
            show_all_invoices(event){
                this.click_view_invoices(this.props.partner);
            }
            click_view_invoices(partner) {
                var self = this;
                var partner_id = partner.id;
                var invoices_for_customer = self.filter_invoices_by_customer(partner_id);
                this.showTempScreen('InvoiceListScreenWidget', {
                    'partner_id': partner_id,
                    'invoices_for_customer': invoices_for_customer
                });
    
            }
            filter_invoices_by_customer(partner_id) {
                var self = this;
                var invoices_for_customer = [];
                self.env.pos.db.pos_all_invoices.forEach(function(invoice) {
                    if (invoice.partner_id[0] == partner_id) {
                        invoices_for_customer.push(invoice);
                    }
                });
                return invoices_for_customer;
            }
        }
    Registries.Component.extend(ClientLine, PosResClientLine);


    class InvoiceListScreenWidget extends PosComponent {

        get_invoices() {
            var self = this;
            return self.props.invoices_for_customer;
        }
        display_invoices(intput_txt) {
            var self = this;
            var all_invoices_for_customer = this.get_invoices();
            var invoices_to_render = all_invoices_for_customer;

            if (intput_txt != undefined && intput_txt != '') {
                var new_invoice_data = [];
                var search_text = intput_txt.toLowerCase()
                all_invoices_for_customer.forEach(function(invoice) {
                    if( invoice.name && invoice.invoice_date && (((invoice.name.toLowerCase()).indexOf(search_text) != -1) || ((invoice.invoice_user_id[1].toLowerCase()).indexOf(search_text) != -1) ||
                        (invoice.invoice_date.toLowerCase()).indexOf(search_text) != -1)) {
                        new_invoice_data = new_invoice_data.concat(invoice);
                    }
                });
                invoices_to_render = new_invoice_data
            }

            var contents = $('div.clientlist-screen.screen')[0].querySelector('.invoice-list-contents');
            contents.innerHTML = "";
            invoices_to_render.forEach(function(invoice) {
                var invoiceline_html = QWeb.render('WkInvoiceLine', {
                    widget: self,
                    invoice: invoice
                });
                var invoiceline = document.createElement('tbody');
                invoiceline.innerHTML = invoiceline_html;
                invoiceline = invoiceline.childNodes[1];
                contents.appendChild(invoiceline);
            });
        }
        keyup_invoice_search(event){
            this.render_list(event.target.value);
        }
        mounted() {
            var self = this;
            super.mounted();
            this.details_visible = false;
            this.display_invoices(undefined);
            $('.invoice-list-contents').delegate('.invoice-line', 'click', function(event) {
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });
            var contents = $('.invoice-details-contents');
            contents.empty();
            var parent = $('.wk_invoice_table').parent();
            parent.scrollTop(0);
        }
        line_select(event, $line, id) {
            var self = this;
            var invoice = self.env.pos.db.invoice_by_id[id];
            if ($line.hasClass('wk_highlight')) {
                $('.wk_invoice_table .wk_highlight').removeClass('wk_highlight');
                $(".invoice-line").css("background-color", "");
                self.display_invoice_details('hide', null);
            } else {
                $('.wk_invoice_table .wk_highlight').removeClass('wk_highlight');
                $(".invoice-line").css("background-color", "");
                $line.addClass('wk_highlight');
                $line.css("background-color", "rgb(110,200,155) !important");
                var y = event.pageY - $line.parent().offset().top;
                self.display_invoice_details('show', invoice, y);
            }
        }
        display_invoice_details(visibility, invoice, clickpos) {
            var self = this;
            var contents = $('.invoice-details-contents');
            var parent = $('.wk_invoice_table').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();
            var invoicelines = [];
            if (visibility == 'show') {
                invoice.invoice_line_ids.forEach(function(line_id) {
                    invoicelines.push(self.env.pos.db.invoice_line_by_id[line_id]);
                });
                contents.empty();
                contents.append($(QWeb.render('InvoiceDetails', { widget: self, invoice: invoice, invoicelines: invoicelines })));
                var new_height = contents.height();
                if (!this.details_visible) {
                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }
                $("#close_invoice_details").on("click", function() {
                    $('.wk_invoice_table .wk_highlight').removeClass('wk_highlight');
                    $(".invoice-line").css("background-color", "");
                    self.display_invoice_details('hide', null);
                });
                this.details_visible = true;
            }
            if (visibility == 'hide') {
                contents.empty();
                if (height > scroll) {
                    contents.css({ height: height + 'px' });
                    contents.animate({ height: 0 }, 400, function() {
                        contents.css({ height: '' });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
                $('.wk_invoice_table .wk_highlight').removeClass('wk_highlight');
                $(".invoice-line").css("background-color", "");
            }
        }
        clickBack(event){
            if(this.props.isShown){
                this.showScreen('ProductScreen');
            }
            else{
                this.showTempScreen('ClientListScreen', { });
            }
        }
    }
    InvoiceListScreenWidget.template = 'InvoiceListScreenWidget';
	Registries.Component.add(InvoiceListScreenWidget);

        

    return {
        InvoiceListScreenWidget: InvoiceListScreenWidget
    }
});