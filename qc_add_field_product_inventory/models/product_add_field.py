# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]

from odoo import fields, models, _,api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight = fields.Float('Net Weight', digits='Stock Weight')
    gross = fields.Float('Gross Weight',digits=(16, 2))
    qty_per_carton = fields.Float('QTY per Carton', digits=(16, 2))
    qty_of_carton = fields.Float('QTY of Carton', digits=(16, 2))


