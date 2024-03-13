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


    @api.onchange('product_template_id')
    def get_volume(self):
        if len(self.product_template_id)>0:
            self.update({
                'width':float(self.product_template_id.breadth) or 0,
                'length': float(self.product_template_id.length) or 0,
                'height': float(self.product_template_id.height) or 0,
                'qty_per_carton': float(self.product_template_id.qty_per_carton) or 0,
                'qty_of_carton': float(self.product_template_id.qty_of_carton) or 0,
                'g_w_kgs': float(self.product_template_id.gross) or 0,
                'n_w_kgs': float(self.product_template_id.weight) or 0,
            })

