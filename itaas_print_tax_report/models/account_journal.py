# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _
class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_undue_tax = fields.Boolean('Is Undue Tax')


class Account_journal(models.Model):
    _inherit = 'account.journal'

    type_vat = fields.Selection([('tax', 'Tax'), ('not_deal', 'Not Due')],string='Type Vat')
