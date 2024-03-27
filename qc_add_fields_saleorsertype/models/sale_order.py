# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_material_bool = fields.Boolean(string="Sale Material")
    sale_production_bool = fields.Boolean(string="Sale Production")
