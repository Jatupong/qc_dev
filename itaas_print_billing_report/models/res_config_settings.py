# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    billing_no_form = fields.Char(string='Billing No. Form')
    show_currency_on_billing = fields.Boolean(string='Show Currency in Billing')
    show_date_auto_billing = fields.Boolean(string='Show Date Billing')
    payment_info = fields.Text(string='Payment Info')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    billing_no_form = fields.Char(related='company_id.billing_no_form', string='Billing No. Form', readonly=False)
    show_currency_on_billing = fields.Boolean(related='company_id.show_currency_on_billing', string='Show Currency in Billing',
                                            readonly=False)
    show_date_auto_billing = fields.Boolean(related='company_id.show_date_auto_billing',
                                              string='Show Date in Billing',
                                              readonly=False)
    payment_info = fields.Text(related='company_id.payment_info', string='Payment Info', readonly=False)