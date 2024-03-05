# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    """
    Add Debit Note wizard: when you want to correct an invoice with a positive amount.
    Opposite of a Credit Note, but different from a regular invoice as you need the link to the original invoice.
    In some cases, also used to cancel Credit Notes
    """
    _inherit = 'account.debit.note'
    _description = 'Add Debit Note wizard'

    def _prepare_default_values(self, move):
        res = super(AccountDebitNote,self)._prepare_default_values(move)
        print ('DEBIT NOTE')
        print('_context:,',self._context)
        invoice_ids = self.env['account.move'].browse(self._context.get('active_ids'))
        for invoice_id in invoice_ids:
            if invoice_id.move_type in ['out_invoice','out_refund']:
                res['is_debit_note'] = True
                res['is_debit_invoice'] = True
            else:
                res['is_debit_note'] = True
                res['is_debit_vendor'] = True
        return res


