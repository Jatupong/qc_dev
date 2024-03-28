# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:28|M:03|Y:2024]

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_cost = fields.Float(string='ผลิตภัณท์', compute='update_product_cost_by_set_line')
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