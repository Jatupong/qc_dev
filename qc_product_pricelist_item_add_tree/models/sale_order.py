# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:02|Y:2024]

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm_sale(self):
        print("action_confirm_sale Action!")
        res = super(SaleOrder, self).action_confirm_sale()
        self.create_pricelist()
        self.update_pricelist_by_order_line()
        self.update_pricelist()
        return res

    # @api.onchange('partner_id')
    def create_pricelist(self):
        print("create_pricelist Action!")
        partner = self.partner_id
        if len(partner) > 0:
            sale_order = partner.sale_order_ids
            so_id = partner.last_website_so_id
            property_product_pricelist = partner.property_product_pricelist
            if property_product_pricelist.public:
                try:
                    self.env['product.pricelist'].create({
                        'name':"Pricelist {}".format(partner.name),
                        'selectable':True,
                    })
                    partner.update({
                            'property_product_pricelist':self.env['product.pricelist'].search([('name', '=', "Pricelist {}".format(partner.name))])
                        })
                    self.update_pricelist_by_order_line()
                except Exception as err:
                    if self.user_has_groups('base.group_no_one'):
                        raise ValidationError(_("Err! {}\nsale_order_ids = {} = last_website_so_id {}\n By Debug mode [Sarawut Ph.]".format(err,len(sale_order),len(so_id))))

    @api.onchange('order_line')
    def update_pricelist_by_order_line(self):
        print("update_pricelist_by_order_line Action!")
        arr = []
        partner = self.partner_id
        if len(partner) > 0:
            property_product_pricelist = partner.property_product_pricelist
            print("property_product_pricelist {}".format(property_product_pricelist.name))
            if len(property_product_pricelist) > 0:
                pricelist_rules_ids = property_product_pricelist.item_ids
                pricelist_rules_ids2 = self.env['product.pricelist'].search(
                [('public', '=', True)],limit=1)

                for sale in self.order_line:
                    # property_product_pricelist.update({"item_ids": self.env['product.pricelist.item'].search([('pricelist_id.id', '=', property_product_pricelist.id)])})
                    chack = len(pricelist_rules_ids.filtered(
                    lambda x: x.product_tmpl_id.name == sale.product_template_id.name))
                    print("chack_{} :{}".format(sale.product_template_id.name,chack))
                    if len(pricelist_rules_ids) == 0:
                        product = self.env['product.template'].search([('name', '=', sale.product_template_id.name)])
                        print("product_id :{}".format(product.name))
                        # base_pricelist_id = self.create_pricelist_item(product, sale, property_product_pricelist)
                        if self.state == 'sale':
                            try:
                                pricelist_rules_ids.create({
                                                            'pricelist_id':property_product_pricelist.id,
                                                              'compute_price': 'formula',
                                                              'base':'pricelist',
                                                              'base_pricelist_id':pricelist_rules_ids2.id,
                                                              'product_tmpl_id': product.id,
                                                              'applied_on': '0_product_variant',
                                                              'product_id': product.product_variant_id.id,
                                                              'currency_id': property_product_pricelist.currency_id.id,
                                                              'product_cost': sale.product_cost,
                                                              'commission_cost': sale.commission_cost,
                                                              'box_cost': sale.box_cost,
                                                              'sticker_cost': sale.sticker_cost,
                                                              'cost_1':sale.cost_1,
                                                              'cost_2': sale.cost_2,
                                                              'cost_3': sale.cost_3,
                                                              })
                                property_product_pricelist.update({"item_ids":self.env['product.pricelist.item'].search([('pricelist_id.id', '=', property_product_pricelist.id)])})
                                # self.update_pricelist()
                            except Exception as err:
                                if self.user_has_groups('base.group_no_one'):
                                    raise ValidationError(_("Err! {}\n By Debug mode [Sarawut Ph.]".format(err)))
                    elif chack != 0:
                        print("sale.product_template_id :{}".format(chack))

                        for pricelist_rules in pricelist_rules_ids:
                            print("TTTT{} = {}".format(pricelist_rules.product_id.name, sale.product_id.name))
                            if pricelist_rules.product_id.name == sale.product_id.name:
                                if self.state == 'sale':
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


    # @api.onchange('partner_id','sale_order_set_line_ids')
    def update_pricelist(self):
        print("update_pricelist Action!")
        msg = "update_pricelist Action!\n"
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


                    #             if pricelist_rules.product_tmpl_id.name == order_set_line_id.product_id.name and self.sale_order.filtered(
                    # lambda x: x.product_template_id.name == pricelist_rules.product_tmpl_id.name):
                                if pricelist_rules.product_tmpl_id.name == order_set_line_id.product_set_id.name:
                                    pricelist_rules.update({'set_line': self.sale_order_set_line_ids.filtered(
                                        lambda x: x.product_set_id.name == pricelist_rules.product_tmpl_id.name)})
                                    print("set_line : {}".format(pricelist_rules.set_line))
                                msg += "Test :{} = {}\n".format(pricelist_rules.product_tmpl_id.name,
                                                                order_set_line_id.product_id.name)
                                msg += "Data:{}\n".format(self.sale_order_set_line_ids.filtered(
                                    lambda x: x.product_set_id.name == pricelist_rules.product_tmpl_id.name))

        if self.user_has_groups('base.group_no_one'):
            raise ValidationError(_(msg))

