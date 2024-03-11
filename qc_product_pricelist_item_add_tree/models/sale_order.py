# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    @api.onchange('order_line','partner_id','sale_order_set_line_ids')
    def update_pricelist(self):
        partner = self.partner_id
        if len(partner) >0:
            property_product_pricelist = partner.property_product_pricelist
            if len(property_product_pricelist)>0:
                pricelist_rules_ids = property_product_pricelist.item_ids
                order_set_line_ids = self.sale_order_set_line_ids
                if len(order_set_line_ids) > 0:
                    if len(pricelist_rules_ids)>0:
                        for order_set_line_id in order_set_line_ids:
                            if len(order_set_line_id.product_id)>0:
                                chack = len(pricelist_rules_ids.filtered(lambda x: x.product_tmpl_id.name == order_set_line_id.product_id.name))
                                print("Len({})".format(chack))
                                if chack==0:
                                    product =self.env['product.template'].search([('name','=',order_set_line_id.product_id.name)])
                                    print("product_id :{}".format(product.name))
                                    try:
                                        pricelist_rules_ids.create({'name': product.display_name,
                                                                    'min_quantity':1,
                                                                    'compute_price':'percentage',
                                                                    'percent_price':10,
                                                                    'applied_on':'1_product',
                                                                    'product_tmpl_id':product.id,
                                                                    'currency_id':property_product_pricelist.currency_id.id,
                                                                    'set_line': self.sale_order_set_line_ids.filtered(
                                                                        lambda
                                                                            x: x.product_id.name == product.name)
                                                                    })
                                        break
                                    except Exception as err:
                                        print("Err! {}".format(err))

                                for pricelist_rules in pricelist_rules_ids:

                                    print("Test :{} = {}".format(pricelist_rules.product_tmpl_id.name,
                                                                 order_set_line_id.product_id.name))

                                    if pricelist_rules.product_tmpl_id.name == order_set_line_id.product_id.name:
                                        pricelist_rules.update({'set_line': self.sale_order_set_line_ids.filtered(
                                            lambda x: x.product_id.name == pricelist_rules.product_tmpl_id.name)})
                                        print("set_line : {}".format(pricelist_rules.set_line))

                elif len(order_set_line_ids) == 0:
                    arr = []
                    for pricelist_rules in pricelist_rules_ids:
                        for set_line in pricelist_rules.set_line:
                            arr.append(set_line.id)

                    self.update({'sale_order_set_line_ids': self.env['sale.order.set.line'].search([('id','in',arr)])})
