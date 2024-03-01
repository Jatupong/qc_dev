# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today (ITAAS)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    branch_no = fields.Char(string='Branch',default='00000')
    customer_no_vat = fields.Boolean(string='Customer No TAX-ID', default=False)
    note_accounting = fields.Text(string='Accounting Note')
    ref = fields.Char(string='Reference', index=True, copy=False)
    bill_to_id = fields.Many2one('res.partner', string='Bill to')

    _sql_constraints = [
        ('uniq_ref_code', 'unique(ref)', "Unique Customer Code"),
    ]
