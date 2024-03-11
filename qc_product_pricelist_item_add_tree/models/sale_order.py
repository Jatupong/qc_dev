# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def create_pricelist(self):
        partner = self.partner_id
        if len(partner) > 0:
            sale_order = partner.sale_order_ids
            so_id = partner.last_website_so_id
            property_product_pricelist = partner.property_product_pricelist
            if len(sale_order) == 0:
                chack = self.env['product.pricelist'].search([('name', '=', "Public Pricelist {}".format(partner.name))])
                try:
                    if len(chack) == 0:
                        property_product_pricelist.create({
                            'name':"Public Pricelist {}".format(partner.name),
                            'selectable':True,
                        })
                        partner.update({
                            'property_product_pricelist':self.env['product.pricelist'].search([('name', '=', "Public Pricelist {}".format(partner.name))])
                        })
                except Exception as err:
                    if self.user_has_groups('base.group_no_one'):
                        raise ValidationError(_("Err! {}\nsale_order_ids = {} = last_website_so_id {}\n By Debug mode [Sarawut Ph.]".format(err,len(sale_order),len(so_id))))


    @api.onchange('order_line')
    def update_pricelist_by_order_line(self):
        arr = []
        partner = self.partner_id
        if len(partner) > 0:
            property_product_pricelist = partner.property_product_pricelist
            if len(property_product_pricelist) > 0:
                pricelist_rules_ids = property_product_pricelist.item_ids
                for sale in self.order_line:
                    chack = len(pricelist_rules_ids.filtered(
                    lambda x: x.product_tmpl_id.name == sale.product_template_id.name))
                    if chack == 0:
                        product = self.env['product.template'].search([('name', '=', sale.product_template_id.name)])
                        base_pricelist_id = self.env['product.pricelist'].search([('name', '=', property_product_pricelist.name)])
                        print("base_pricelist_id :{}".format(base_pricelist_id.name))
                        print("product_id :{}".format(product.name))
                        try:
                              pricelist_rules_ids.create({'name': product.display_name,
                                                          # 'min_quantity': 1,
                                                          'compute_price': 'formula',
                                                          'base':'pricelist',
                                                          'base_pricelist_id':base_pricelist_id.id ,
                                                          # 'percent_price': 10,
                                                          # 'applied_on': '1_product',
                                                          'product_tmpl_id': product.id,
                                                          'applied_on': '0_product_variant',
                                                          'product_id': product.product_variant_id.id,
                                                          # 'product_id': product.product_variant_id or product.id,
                                                          'currency_id': property_product_pricelist.currency_id.id,
                                                          'product_cost': sale.product_cost,
                                                          'commission_cost': sale.commission_cost,
                                                          'box_cost': sale.box_cost,
                                                          'sticker_cost': sale.sticker_cost,
                                                          'cost_1':sale.cost_1,
                                                          'cost_2': sale.cost_2,
                                                          'cost_3': sale.cost_3,


                                                          })
                              self.update_pricelist()
                        except Exception as err:
                            if self.user_has_groups('base.group_no_one'):
                                raise ValidationError(_("Err! {}\n By Debug mode [Sarawut Ph.]".format(err)))
                    elif chack != 0:
                        print("sale.product_template_id :{}".format(chack))
                        for pricelist_rules in pricelist_rules_ids:
                            if pricelist_rules.product_tmpl_id.name == sale.product_template_id.name:
                                try:
                                    pricelist_rules_ids.update({
                                        'currency_id': property_product_pricelist.currency_id.id,
                                        'product_cost': sale.product_cost,
                                        'commission_cost': sale.commission_cost,
                                        'box_cost': sale.box_cost,
                                        'sticker_cost': sale.sticker_cost,
                                        'cost_1': sale.cost_1,
                                        'cost_2': sale.cost_2,
                                        'cost_3': sale.cost_3,
                                    })
                                except Exception as err:
                                    print("TwT :{} = {}".format(pricelist_rules.product_tmpl_id.name,
                                                                sale.product_template_id.name))
                                    if self.user_has_groups('base.group_no_one'):
                                        raise ValidationError(_("Err! {}\n By Debug mode [Sarawut Ph.]".format(err)))

                                for set_line in pricelist_rules.set_line:
                                    arr.append(set_line.id)

        print("Arr {}".format(arr))
        self.update({'sale_order_set_line_ids': self.env['sale.order.set.line'].search([('id', 'in', arr)])})


    @api.onchange('partner_id','sale_order_set_line_ids')
    def update_pricelist(self):
        partner = self.partner_id
        if len(partner) >0:
            property_product_pricelist = partner.property_product_pricelist
            if len(property_product_pricelist)>0:
                pricelist_rules_ids = property_product_pricelist.item_ids
                order_set_line_ids = self.sale_order_set_line_ids
                if len(order_set_line_ids) > 0:
                    for order_set_line_id in order_set_line_ids:
                        if len(order_set_line_id.product_id) > 0:
                            for pricelist_rules in pricelist_rules_ids:

                                print("Test :{} = {}".format(pricelist_rules.product_tmpl_id.name,
                                                             order_set_line_id.product_id.name))

                                if pricelist_rules.product_tmpl_id.name == order_set_line_id.product_id.name and self.sale_order.filtered(
                    lambda x: x.product_template_id.name == pricelist_rules.product_tmpl_id.name):
                                    pricelist_rules.update({'set_line': self.sale_order_set_line_ids.filtered(
                                        lambda x: x.product_id.name == pricelist_rules.product_tmpl_id.name)})
                                    print("set_line : {}".format(pricelist_rules.set_line))
