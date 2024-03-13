# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]


from odoo import fields, models, _,api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_per_carton = fields.Float('QTY per Carton', digits=(16, 2))
    qty_of_carton = fields.Float('QTY of Carton', digits=(16, 2))

    # qty_per_carton = fields.Float('QTY per Carton', digits=(16, 2),related="product_template_id.qty_per_carton")
    # qty_of_carton = fields.Float('QTY of Carton', digits=(16, 2),related="product_template_id.qty_of_carton")
    # width = fields.Float(string='Width',related="product_template_id.breadth")
    # length = fields.Float(string='Length',related="product_template_id.length")
    # height = fields.Float(string='Height',related="product_template_id.height")
    # g_w_kgs = fields.Float(related="product_template_id.gross")
    # n_w_kgs = fields.Float(related="product_template_id.weight")


    @api.onchange('product_id')
    def get_volume(self):
        if len(self.product_id)>0:
            print("self.product_id",self.product_id)
            pricelist_rule_id = self.order_id.pricelist_id._get_product_rule(
                    self.product_id,
                    self.product_uom_qty or 1.0,
                    uom=self.product_uom,
                    date=self.order_id.date_order,)
            print("pricelist_rule {}".format(pricelist_rule_id))
            self.update({
                'width':float(self.product_template_id.breadth) or 0,
                'length': float(self.product_template_id.length) or 0,
                'height': float(self.product_template_id.height) or 0,
                'qty_per_carton': float(self.product_template_id.qty_per_carton) or 0,
                'qty_of_carton': float(self.product_template_id.qty_of_carton) or 0,
                'g_w_kgs': float(self.product_template_id.gross) or 0,
                'n_w_kgs': float(self.product_template_id.weight) or 0,
            })
            pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_rule_id)
            self.update({
                'product_cost': pricelist_rule.product_cost,
                'commission_cost': pricelist_rule.commission_cost,
                'box_cost': pricelist_rule.box_cost,
                'sticker_cost': pricelist_rule.sticker_cost,
                'cost_1': pricelist_rule.cost_1,
                'cost_2': pricelist_rule.cost_2,
                'cost_3': pricelist_rule.cost_3,
            })

            # partner = self.partner_id
            # if len(partner) > 0:
            #     property_product_pricelist = partner.property_product_pricelist
            #     if len(property_product_pricelist) > 0:
            #         pricelist_rules_ids = property_product_pricelist.item_ids
            #         for pricelist_rules in pricelist_rules_ids:
            #             if pricelist_rules.product_id.name == self.product_id.name:
            #                 self.update({
            #                     'product_cost': pricelist_rules.product_cost,
            #                     'commission_cost': pricelist_rules.commission_cost,
            #                     'box_cost': pricelist_rules.box_cost,
            #                     'sticker_cost': pricelist_rules.sticker_cost,
            #                     'cost_1':pricelist_rules.cost_1,
            #                     'cost_2': pricelist_rules.cost_2,
            #                     'cost_3': pricelist_rules.cost_3,
            #                 })


