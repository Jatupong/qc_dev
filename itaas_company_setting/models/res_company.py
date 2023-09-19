# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class ResCompany(models.Model):
    _inherit ="res.company"

    system_version = fields.Char(string='System Version', default='13.0.1')
    release_date = fields.Date(string='Release Date',default='2020-07-01')
    show_product_code_on_invoice = fields.Boolean('Show Code in Invoice')
    description_on_invoice = fields.Char('Description')
    payment_info_invoice = fields.Char('Payment Info')
    payment_info_invoice2 = fields.Char('Payment Info (2)')
    check_customer_tax_id = fields.Selection([('sale','Sale Order'),('invoice','Invoice')],string='Check Customer Tax',default='sale')