#-*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import datetime, date
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime, timedelta


class account_move_reversal(models.TransientModel):
    _inherit = "account.move.reversal"

    credit_note_reason = fields.Many2one('credit.note.reason', string='Credit Note Reason')

    def _prepare_default_reversal(self, move):
        res = super(account_move_reversal, self)._prepare_default_reversal(move)
        res['ref']= _('Reversal of: %s, %s') % (move.name, self.credit_note_reason.name) if self.credit_note_reason else _('Reversal of: %s') % (move.name),
        res.update({'credit_note_reason': self.credit_note_reason.id})
        return res


class account_debit_note(models.TransientModel):
    _inherit = "account.debit.note"

    credit_note_reason = fields.Many2one('credit.note.reason', string='Debit Note Reason')

    def _prepare_default_values(self, move):
        res = super(account_debit_note, self)._prepare_default_values(move)
        # res['ref']= _('Reversal of: %s, %s') % (move.name, self.credit_note_reason.name) if self.credit_note_reason else _('Reversal of: %s') % (move.name),
        res.update({'credit_note_reason': self.credit_note_reason.id})
        return res


