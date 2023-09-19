/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_receipt_design.models', function (require) {
    "use strict"
    var { PosGlobalState, Order } = require('point_of_sale.models');
    var PosDB = require("point_of_sale.DB");
    const Registries = require('point_of_sale.Registries');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const { nextFrame } = require('point_of_sale.utils');
    var field_utils = require('web.field_utils');
    const { onMounted } = owl;

    PosDB.include({
        init: function (options) {
            var self = this;
            this._super(options);
            this.receipt_design = null;
        },
    })

    const PosReceipt = (Order) => class PosReceipt extends Order {
        constructor(attributes, options) {
            super(...arguments)
            if (!this.validation_date) {
                this.validation_date = field_utils.format.datetime(moment(this.creation_date), {}, { timezone: false });
            }
        }
    }
    Registries.Model.extend(Order, PosReceipt);

    const PosRestaurantDesign = (PosGlobalState) => class PosRestaurantDesign extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            this._loadReceiptDesign(loadedData['receipt.design']);
        }
        _loadReceiptDesign(designs) {
            this.db.all_designs = designs;
            var receipt_by_id = {};
            designs.forEach(function (design) {
                receipt_by_id[design.id] = design;
            });
            this.db.receipt_by_id = receipt_by_id;
        }
    }
    Registries.Model.extend(PosGlobalState, PosRestaurantDesign);

    // Inherit AbstractReceiptScreen
    const PosResAbstractReceiptScreen = (AbstractReceiptScreen) => class extends AbstractReceiptScreen {
        async printReceipt() {
            var self = this;
            if (!self.env.pos.config.use_custom_receipt) {
                var data = super._printReceipt();
                return data
            } else {
                if (self.env.pos.proxy.printer) {
                    var receipt_design_id = self.env.pos.config.receipt_design_id[0]
                    var receipt_design = self.env.pos.db.receipt_by_id[receipt_design_id].receipt_design
                    var order = self.env.pos.get_order();

                    var data = {
                        widget: self.env,
                        pos: order.pos,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order.get_orderlines(),
                        paymentlines: order.get_paymentlines(),
                        moment: moment, };

                    var parser = new DOMParser();
                    var xmlDoc = parser.parseFromString(receipt_design, "text/xml");

                    var s = new XMLSerializer();
                    var newXmlStr = s.serializeToString(xmlDoc);

                    //Works using the DOMParser
                    var qweb = new QWeb2.Engine();
                    qweb.add_template('<templates><t t-name="receipt_design">' + newXmlStr + '</t></templates>');

                    var receipt = qweb.render('receipt_design', data);

                    const printResult = await self.env.pos.proxy.printer.print_receipt(receipt);
                    if (printResult.successful) {
                        return true;
                    } else {
                        const { confirmed } = await self.showPopup('ConfirmPopup', {
                            title: printResult.message.title,
                            body: 'Do you want to print using the web printer?',
                        });
                        if (confirmed) {
                            await nextFrame();
                            return await self._printWeb();
                        }
                        return false;
                    }
                } else {
                    return await self._printWeb();
                }
            }
        }
    }
    Registries.Component.extend(AbstractReceiptScreen, PosResAbstractReceiptScreen);

    // Inherit OrderReceipt
    const PosResOrderReceipt = (OrderReceipt) => class extends OrderReceipt {
        setup() {
            super.setup();
            onMounted(() => {
                var self = this;
                if (self.env.pos.config.use_custom_receipt) {
                    var receipt_design_id = self.env.pos.config.receipt_design_id[0]
                    var receipt_design = self.env.pos.db.receipt_by_id[receipt_design_id].receipt_design
                    var order = self._receiptEnv.order;

                    var data = { widget: self.env,
                        pos: order.pos,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order.get_orderlines(),
                        paymentlines: order.get_paymentlines(),
                        moment: moment, };

                    var parser = new DOMParser();
                    var xmlDoc = parser.parseFromString(receipt_design, "text/xml");
    
                    var s = new XMLSerializer();
                    var newXmlStr = s.serializeToString(xmlDoc);

                    //Works using the DOMParser
                    var qweb = new QWeb2.Engine();
                    qweb.add_template('<templates><t t-name="receipt_design">'+newXmlStr+'</t></templates>');

                    var receipt = qweb.render('receipt_design',data) ;
                    $('div.pos-receipt').replaceWith(receipt);
                }
            })
        }
    }
    Registries.Component.extend(OrderReceipt, PosResOrderReceipt);
});
