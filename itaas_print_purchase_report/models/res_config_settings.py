# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_order_no_form = fields.Char(string='Purchase Order No. Form')
    show_product_code_on_purchase = fields.Boolean(string='Show Code in Purchase')
    show_currency_on_purchase = fields.Boolean(string='Show Currency in Purchase')
    show_date_auto_purchase = fields.Boolean(string='Show Date Purchase')

    document_id = fields.Char(string='ฟอร์มเคลมสินค้าใบส่งสินค้า')
    document_id2 = fields.Char(string='ฟอร์มเคลมสินค้าใบเบิกพัสดุ')
    document_id3 = fields.Char()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_order_no_form = fields.Char(related='company_id.purchase_order_no_form', string='Purchase Order No. Form', readonly=False)
    show_product_code_on_purchase = fields.Boolean(related='company_id.show_product_code_on_purchase', string='Show Code in Purchase', readonly=False)
    show_currency_on_purchase = fields.Boolean(related='company_id.show_currency_on_purchase', string='Show Currency in Purchase', readonly=False)
    show_date_auto_purchase = fields.Boolean(related='company_id.show_date_auto_purchase', string='Show Date Purchase', readonly=False)

    document_id = fields.Char(related='company_id.document_id',string='ฟอร์มเคลมสินค้าใบส่งสินค้า', readonly=False)
    document_id2 = fields.Char(related='company_id.document_id2', string='ฟอร์มเคลมสินค้าใบเบิกพัสดุ', readonly=False)
    document_id3 = fields.Char(related='company_id.document_id3', string='sss_2', readonly=False)