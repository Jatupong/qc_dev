# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    quotation_no_form = fields.Char(string='Quotation No. Form')
    sale_order_no_form = fields.Char(string='Sales Order No. Form')
    show_product_code_on_sale = fields.Boolean(string='Show Code in Quote')
    show_currency_on_sale = fields.Boolean(string='Show Currency in Quote')
    show_date_auto_sale = fields.Boolean(string='Show Date Quote')
    standard_tax = fields.Integer(string='Standard Tax %', default=7)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quotation_no_form = fields.Char(related='company_id.quotation_no_form', string='Quotation No. Form', readonly=False)
    sale_order_no_form = fields.Char(related='company_id.sale_order_no_form', string='Sales Order No. Form', readonly=False)
    show_product_code_on_sale = fields.Boolean(related='company_id.show_product_code_on_sale', string='Show Code in Quote', readonly=False)
    show_currency_on_sale = fields.Boolean(related='company_id.show_currency_on_sale', string='Show Currency in Quote', readonly=False)
    show_date_auto_sale = fields.Boolean(related='company_id.show_date_auto_sale', string='Show Date Quote', readonly=False)
    standard_tax = fields.Integer(related='company_id.standard_tax', string='Standard Tax %', default=7, readonly=False)