# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    name = fields.Char(compute="_compute_name_by_sequence")

    @api.depends("state", "journal_id", "date")
    def _compute_name_by_sequence(self):
        print('_compute_name_by_sequence:')
        for move in self:
            name = move.name or "/"
            if (
                    move.state == "posted"
                    and (not move.name or move.name == "/")
                    and move.journal_id
                    and move.journal_id.sequence_id
            ):
                if (
                        move.move_type in ("out_refund", "in_refund")
                        and move.journal_id.type in ("sale", "purchase")
                        and move.journal_id.refund_sequence
                        and move.journal_id.refund_sequence_id
                ):
                    print('iFFFFFFFFFFF')
                    seq = move.journal_id.refund_sequence_id
                else:
                    print('ELSEEEE',move)
                    seq = move.journal_id.sequence_id
                name = seq.with_context(ir_sequence_date=move.date).next_by_id()

            move.name = name

    def _constrains_date_sequence(self):
        return True

