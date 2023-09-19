# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Ying)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contact_id = fields.Many2one('res.partner', string="Contact")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        invoice_vals.update({'contact_id': self.contact_id.id})

        return invoice_vals