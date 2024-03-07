# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]

from odoo import api, fields, models, _


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    Test=fields.Many2many("sale.order.set.line",string="Set line")