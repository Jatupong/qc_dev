# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Ying)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    contact_id = fields.Many2one('res.partner', string="Contact")

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        if not self.purchase_id:
            return res

        self.contact_id = self.purchase_id.contact_id.id

        return res

