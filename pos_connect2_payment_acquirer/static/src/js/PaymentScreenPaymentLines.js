odoo.define('pos_connect.PaymentScreenPaymentLines', function (require) {
    'use strict';

    const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreenPaymentLines');
    const Registries = require('point_of_sale.Registries');

    const PosConnectPaymentLines = (PaymentScreenPaymentLines) =>
        class extends PaymentScreenPaymentLines {
            /**
             * @override
             */
            selectedLineClass(line) {
                console.log("line",line.connect_payment_pending)
                return Object.assign({}, super.selectedLineClass(line), {
                    o_pos_connect_scan_pending: line.connect_payment_pending,
                });
            }
            /**
             * @override
             */
            unselectedLineClass(line) {
                return Object.assign({}, super.unselectedLineClass(line), {
                    o_pos_connect_scan_pending: line.connect_payment_pending,
                });
            }
        };

    Registries.Component.extend(PaymentScreenPaymentLines, PosConnectPaymentLines);

    return PaymentScreenPaymentLines;
});
