# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from odoo.exceptions import UserError, AccessError


class AccountMoveseq(models.Model):
    _inherit = 'account.move'

    is_debit_note = fields.Boolean(string='Is Debit Note',default=False)
    is_debit_invoice = fields.Boolean(string='Is Debit Invoice')
    is_debit_vendor = fields.Boolean(string='Is Debit Vendor', default=False)
    is_credit_note = fields.Boolean(string='Is Credit Note')

    def _get_sequence(self):
        print('mmmmmm')
        print('_get_sequence')
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''

        self.ensure_one()
        journal = self.journal_id
        # res = super(AccountMoveseq, self)._get_sequence()
        # print('move_type',self.move_type)
        # print('_get_sequence',self.is_debit_note)
        if self.move_type in ('out_invoice', 'in_invoice') and self.is_debit_note and journal.debit_sequence_id:
            return journal.debit_sequence_id
        if self.move_type in ('out_refund', 'in_refund') and self.is_credit_note and journal.refund_sequence_id:
            return journal.refund_sequence_id
        return

