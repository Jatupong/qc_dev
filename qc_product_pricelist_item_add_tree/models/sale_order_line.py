# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:28|M:03|Y:2024]

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_cost = fields.Float(string='ผลิตภัณท์', compute='update_product_cost_by_set_line')
    commission_cost = fields.Float(string='คอม',compute='update_commission_cost_by_set_line')
    box_cost = fields.Float(string='กล่อง',compute='update_box_cost_by_set_line')
    sticker_cost = fields.Float(string='สติ๊กเกอร์',compute='update_sticker_cost_by_set_line')
    cost_1 = fields.Float(string='ราคา1',compute='update_cost_1_by_set_line')
    cost_2 = fields.Float(string='ราคา2',compute='update_cost_2_by_set_line')
    cost_3 = fields.Float(string='ราคา3',compute='update_cost_3_by_set_line')


    def update_cost_3_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.cost_3
                    line.update({
                        'cost_3':zum
                    })
                else:
                    line.update({
                        'cost_3': 0
                    })
            else:
                pass
    def update_cost_2_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.cost_2
                    line.update({
                        'cost_2':zum
                    })
                else:
                    line.update({
                        'cost_2': 0
                    })
            else:
                pass
    def update_cost_1_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.cost_1
                    line.update({
                        'cost_1':zum
                    })
                else:
                    line.update({
                        'cost_1': 0
                    })
            else:
                pass
    def update_sticker_cost_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.sticker_cost
                    line.update({
                        'sticker_cost':zum
                    })
                else:
                    line.update({
                        'sticker_cost': 0
                    })
            else:
                pass
    def update_box_cost_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.box_cost
                    line.update({
                        'box_cost':zum
                    })
                else:
                    line.update({
                        'box_cost': 0
                    })
            else:
                pass

    def update_commission_cost_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.commission_cost
                    line.update({
                        'commission_cost':zum
                    })
                else:
                    line.update({
                        'commission_cost': 0
                    })
            else:
                pass
    def update_product_cost_by_set_line(self):
        for line in self:
            if line.order_id:
                if len(line.order_id.sale_order_set_line_ids)>0:
                    zum = 0
                    set_line = line.order_id.sale_order_set_line_ids.filtered(lambda x: x.product_set_id.id == line.product_id.id)
                    for set in set_line:
                        zum+= set.product_cost
                    line.update({
                        'product_cost':zum
                    })
                else:
                    line.update({
                        'product_cost': 0
                    })
            else:
                pass