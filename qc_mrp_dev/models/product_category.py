# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError
from datetime import datetime, date

class product_category(models.Model):
    _inherit = "product.category"

    max_capacity = fields.Float(string='Max Capacity')
    is_plan_color = fields.Boolean(string='Plan/Color')
    product_line = fields.Boolean(string='Product Line')


