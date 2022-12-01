# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError
from datetime import datetime, date

class product_template(models.Model):
    _inherit = "product.template"

    product_category_line_id = fields.Many2one('product.category',string='แยกตามกลุ่มผลิตภัณฑ์')
    product_plan_colour_id = fields.Many2one('product.category',string='Plan/Color')
    decoration_id = fields.Many2one('product.category',string='Decoration')


