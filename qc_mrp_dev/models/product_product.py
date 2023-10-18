# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError
from datetime import datetime, date

class product_product(models.Model):
    _inherit = "product.product"

    shape_name_eng = fields.Char(string='ShapeEng')
    shape_name_th = fields.Char(string='ShapeThai')


