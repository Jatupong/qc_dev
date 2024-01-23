# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _
# from bahttext import bahttext
from odoo.exceptions import UserError
import math


class account_move(models.Model):
    _inherit = "account.move"
    _order = 'date asc'

    wht_personal_company = fields.Selection([('personal', 'ภงด3'), ('company', 'ภงด53'),('50-1', 'ภงด1')],string="WHT Type")
    is_beginning_balance =fields.Boolean(string='Beginning Balance',default=False)
    is_year_end = fields.Boolean(string='Year End', default=False)
    amount = fields.Text('Amount')

    # def baht_text(self, amount_total):
    #     return bahttext(amount_total)


    # @api.onchange('is_beginning_balance')
    # def onchange_beginning_balance(self):
    #     for move in self:
    #         for line in move.line_ids:
    #             line.is_beginning_balance = move.is_beginning_balance


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = 'debit desc'

    is_beginning_balance = fields.Boolean(string='Beginning Balance',related='move_id.is_beginning_balance',store=True,default=False)
    is_year_end = fields.Boolean(string='Year End', related='move_id.is_year_end',store=True,default=False)
    account_move_credit = fields.Char(related="account_id.code")
    
    
    @api.onchange('wht_tax')
    def _onchange_wht_tax(self):
        self.wht_type = self.wht_tax.wht_type
