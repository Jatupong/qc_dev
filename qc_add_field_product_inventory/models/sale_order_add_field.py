# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]


from odoo import fields, models, _,api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_per_carton = fields.Float('QTY per Carton', digits=(16, 2),related="product_template_id.qty_per_carton")
    qty_of_carton = fields.Float('QTY of Carton', digits=(16, 2),related="product_template_id.qty_of_carton")
    # width = fields.Float(string='Width',related="product_template_id.breadth_int")
    # length = fields.Float(string='Length',related="product_template_id.length_int")
    # height = fields.Float(string='Height',related="product_template_id.height_int")
    g_w_kgs = fields.Float(related="product_template_id.gross")
    n_w_kgs = fields.Float(related="product_template_id.weight")

    @api.onchange('product_template_id')
    def get_volume(self):
        if self.product_template_id:
            self.update({
                'width':int(self.product_template_id.breadth) or 0,
                'length': int(self.product_template_id.length) or 0,
                'height': int(self.product_template_id.height) or 0,
            })
