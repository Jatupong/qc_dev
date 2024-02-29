# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'


    tax_inv_generated = fields.Boolean(string='Tax Invoice Generated',copy=False)
    tax_invoice_date = fields.Date(string='Tax Invoice Date',copy=False)
    tax_inv_number = fields.Char(string='Tax Invoice Number',copy=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    amount_before_tax = fields.Float(string='Amt Before Tax')
    tax_inv_date = fields.Date(string="Tax Inv Date", related="move_id.tax_invoice_date")
    date_vat_new = fields.Date(string="Date Vat", copy=False)
    is_special_tax = fields.Boolean(string='Special Tax', copy=False)