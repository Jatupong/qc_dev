# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_set = fields.Boolean(string='Product Set')
    product_set_lines = fields.One2many('product.set.detail','product_template_id',string='Product Set Detail')

class ProductSetDetail(models.Model):
    _name = 'product.set.detail'

    product_id = fields.Many2one('product.product',string='Product')
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom',string='Unit of Measure')
    product_template_id = fields.Many2one('product.template',string='Product Template')
