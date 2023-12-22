odoo.define('tis_custom_loyalty.Models', function (require) {
    'use strict';


   var { PosGlobalState, Order } = require('point_of_sale.models');
   const { PosLoyaltyOrder } = require('@pos_loyalty/js/Loyalty');
   const Registries = require('point_of_sale.Registries');
   console.log("PosLoyaltyOrder",PosLoyaltyOrder)
   const { round_decimals, round_precision } = require('web.utils');

   const PosPosGlobalState = (PosGlobalState) => class PosPosGlobalState extends PosGlobalState {

      async _processData(loadedData) {
        await super._processData(...arguments);
             this.rules = loadedData['loyalty.rule'] || [];
            this._loadLoyaltyDataNew();

        }

     _loadLoyaltyDataNew() {
        for (const rule of this.rules) {
            rule.valid_partner_ids = new Set(rule.valid_partner_ids);
            }
        }
    }
    Registries.Model.extend(PosGlobalState, PosPosGlobalState);



    const PosOrder = (Order) => class PosOrder extends Order {

     pointsForPrograms(programs) {
        console.log("programs",programs)
        const customer = this.get_partner()
        console.log("customer",customer)
        const totalTaxed = this.get_total_with_tax();
        const totalUntaxed = this.get_total_without_tax();
        const totalsPerProgram = Object.fromEntries(programs.map((program) => [program.id, {'untaxed': totalUntaxed, 'taxed': totalTaxed}]));
        const orderLines = this.get_orderlines();
        for (const line of orderLines) {
            if (!line.reward_id) {
                continue;
            }
            const reward = this.pos.reward_by_id[line.reward_id];
            if (reward.reward_type !== 'discount') {
                continue;
            }
            const rewardProgram = reward.program_id;
            for (const program of programs) {
                // Remove automatic discount and this program's discounts from the totals.
                if (program.id === rewardProgram.id || rewardProgram.trigger === 'auto') {
                    totalsPerProgram[program.id]['taxed'] -= line.get_price_with_tax();
                    totalsPerProgram[program.id]['untaxed'] -= line.get_price_without_tax();
                }
            }
        }
        const result = {}
        for (const program of programs) {
            let points = 0;
            const splitPoints = [];
            for (const rule of program.rules) {
                if (rule.mode === 'with_code' && !this.codeActivatedProgramRules.includes(rule.id)) {
                    continue;
                }
                const amountCheck = rule.minimum_amount_tax_mode === 'incl' && totalsPerProgram[program.id]['taxed'] || totalsPerProgram[program.id]['untaxed'];
                if (rule.minimum_amount > amountCheck) { // NOTE: big doutes par rapport au fait de compter tous les produits
                    continue;
                }
                let totalProductQty = 0;
                // Only count points for paid lines.
                const qtyPerProduct = {};
                let orderedProductPaid = 0;
                for (const line of orderLines) {
                    if (((!line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.get_product().id))) ||
                        (line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.reward_product_id)))) &&
                         customer && (customer.id && (rule.any_partner || rule.valid_partner_ids.has(customer.id))) &&
                        !line.ignoreLoyaltyPoints({ program })){
                        // We only count reward products from the same program to avoid unwanted feedback loops
                        if (line.reward_product_id) {
                            const reward = this.pos.reward_by_id[line.reward_id];
                            if (program.id !== reward.program_id) {
                                continue;
                            }
                        }
                        const lineQty = (line.reward_product_id ? -line.get_quantity() : line.get_quantity());
                        totalProductQty += lineQty;
                        if (qtyPerProduct[line.reward_product_id || line.get_product().id]) {
                            qtyPerProduct[line.reward_product_id || line.get_product().id] += lineQty;
                        } else {
                            qtyPerProduct[line.reward_product_id || line.get_product().id] = lineQty;
                        }
                        orderedProductPaid += line.get_price_with_tax();
                    }
                }
                if (totalProductQty < rule.minimum_qty) {
                    // Should also count the points from negative quantities.
                    // For example, when refunding an ewallet payment. See TicketScreen override in this addon.
                    continue;
                }
                if (program.applies_on === 'future' && rule.reward_point_split && rule.reward_point_mode !== 'order') {
                    // In this case we count the points per rule
                    if (rule.reward_point_mode === 'unit') {
                        splitPoints.push(...Array.apply(null, Array(totalProductQty)).map((_) => {return {points: rule.reward_point_amount}}));
                    } else if (rule.reward_point_mode === 'money') {
                        for (const line of orderLines) {
                            if (line.is_reward_line || !(rule.valid_product_ids.has(line.get_product().id)) || line.get_quantity() <= 0
                                || line.ignoreLoyaltyPoints({ program })) {
                                continue;
                            }
                            const pointsPerUnit = round_precision(rule.reward_point_amount * line.get_price_with_tax() / line.get_quantity(), 0.01);
                            if (pointsPerUnit > 0) {
                                splitPoints.push(...Array.apply(null, Array(line.get_quantity())).map(() => {
                                    if (line.giftBarcode && line.get_quantity() == 1) {
                                        return {points: pointsPerUnit, barcode: line.giftBarcode, giftCardId: line.giftCardId };
                                    }
                                    return {points: pointsPerUnit}
                                }));
                            }
                        }
                    }
                } else {
                    // In this case we add on to the global point count
                    if (rule.reward_point_mode === 'order') {
                        points += rule.reward_point_amount;
                    } else if (rule.reward_point_mode === 'money') {
                        // NOTE: unlike in sale_loyalty this performs a round half-up instead of round down
                        points += round_precision(rule.reward_point_amount * orderedProductPaid, 0.01);
                    } else if (rule.reward_point_mode === 'unit') {
                        points += rule.reward_point_amount * totalProductQty;
                    }
                }
            }
            const res = points ? [{points}] : [];
            if (splitPoints.length) {
                res.push(...splitPoints);
            }
            result[program.id] = res;
        }
        return result;
    }
    }
    Registries.Model.extend(Order, PosOrder);
});