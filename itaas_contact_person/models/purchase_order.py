# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Ying)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    contact_id = fields.Many2one('res.partner', string="Contact")