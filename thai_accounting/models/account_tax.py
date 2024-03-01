# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _


class account_wht_type(models.Model):
    _name = 'account.wht.type'
    _description = "Account WHT Type"

    name = fields.Char(string='WHT Type')
    is_wht_2 = fields.Boolean('WHT 2')
        # sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence',
    #                               help="This field contains the information related to the numbering of the journal entries of this journal.",
    #                               required=True, copy=False)

class Account_Tax(models.Model):
    _inherit = 'account.tax'

    wht = fields.Boolean(string="WHT")
    wht_type = fields.Many2one('account.wht.type', string='WHT Type')
    tax_report = fields.Boolean(string="Tax Report")
    tax_no_refund = fields.Boolean(string="Tax No Refund")
