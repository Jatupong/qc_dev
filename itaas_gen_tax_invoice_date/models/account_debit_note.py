# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountDebitNotedev(models.TransientModel):

    _inherit = 'account.debit.note'

    def create_debit(self):
        res = super().create_debit()
        new_move_id = res.get('res_id')
        if new_move_id:
            new_move = self.env['account.move'].browse(new_move_id)
            new_move.is_debit_note = True
        return res
