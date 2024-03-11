# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]

from odoo import api, fields, models, _


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    set_line=fields.Many2many("sale.order.set.line",string="Set line")
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    height = fields.Float(string='Height')
    product_cost = fields.Float(string='ผลิตภัณท์')
    commission_cost = fields.Float(string='คอม')
    box_cost = fields.Float(string='กล่อง')
    sticker_cost = fields.Float(string='สติ๊กเกอร์')
    cost_1 = fields.Float(string='ราคา1')
    cost_2 = fields.Float(string='ราคา2')
    cost_3 = fields.Float(string='ราคา3')
    g_w_kgs = fields.Float(string='G.W. KGS.')
    n_w_kgs = fields.Float(string='N.W. KGS.')