# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.

from odoo import api, fields, models, _


class SaleQuotation(models.Model):
    _inherit = 'sale.order'


    department = fields.Char(string='แผนก')
    id_pp = fields.Char(string='รหัส PP')
    id_po = fields.Char(string='รหัสPO')
    w_load_product = fields.Char(string='Wโหลดสินค้า')
    box_type = fields.Char(string='Box Type')
    download_with = fields.Char(string='Download With')

    correction = fields.Char(string='Correction')
    currency = fields.Char(string='Currency')
    container = fields.Char(string='Container')
    loading_type = fields.Char(string='Loading Type')
    bar_code = fields.Char(string='Bar Code')
