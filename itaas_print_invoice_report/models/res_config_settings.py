# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_no_form = fields.Char(string='Invoice No. Form')
    invoice_and_tax_invoice_no_form = fields.Char(string='Invoice & Tax No. Form')
    tax_invoice_no_form = fields.Char(string='Tax Invoice No. Form')
    receipt_no_form = fields.Char(string='Receipt No. Form')
    tax_invoice_and_receipt_no_form = fields.Char(string='Tax Invoice & Receipt No. Form')
    credit_no_form = fields.Char(string='Credit Note No. Form')
    debit_no_form = fields.Char(string='Debit Note No. Form')
    down_payment_no_form = fields.Char(string='Down Payment No. Form')
    invoice_billing_no_form = fields.Char(string='Invoice Billing No. Form', readonly=False)
    show_currency_on_invoice = fields.Boolean(string='Show Currency in Invoice')
    show_date_auto_invoice = fields.Boolean(string='Show Date Invoice')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_no_form = fields.Char(related='company_id.invoice_no_form', string='Invoice No. Form', readonly=False)
    invoice_and_tax_invoice_no_form = fields.Char(related='company_id.invoice_and_tax_invoice_no_form', string='Invoice & Tax No. Form', readonly=False)
    tax_invoice_no_form = fields.Char(related='company_id.tax_invoice_no_form', string='Tax Invoice No. Form', readonly=False)
    receipt_no_form = fields.Char(related='company_id.receipt_no_form', string='Receipt No. Form', readonly=False)
    tax_invoice_and_receipt_no_form = fields.Char(related='company_id.tax_invoice_and_receipt_no_form', string='Tax Invoice & Receipt No. Form', readonly=False)
    credit_no_form = fields.Char(related='company_id.credit_no_form', string='Credit Note No. Form', readonly=False)
    debit_no_form = fields.Char(related='company_id.debit_no_form', string='Debit No. Note Form', readonly=False)
    down_payment_no_form = fields.Char(related='company_id.down_payment_no_form', string='Down Payment No. Form', readonly=False)
    invoice_billing_no_form = fields.Char(related='company_id.invoice_billing_no_form', string='Invoice Billing No. Form', readonly=False)
    show_currency_on_invoice = fields.Boolean(related='company_id.show_currency_on_invoice', string='Show Currency in Invoice', readonly=False)
    show_date_auto_invoice = fields.Boolean(related='company_id.show_date_auto_invoice', string='Show Date Invoice', readonly=False)