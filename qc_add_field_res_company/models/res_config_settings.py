# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_request_form = fields.Char(string='Purchase Request')
    document_id4 = fields.Char()

    document_id5 = fields.Char()
    document_id6 = fields.Char()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_request_form = fields.Char(related='company_id.purchase_request_form', string='Purchase Request', readonly=False)
    document_id4 = fields.Char(related='company_id.document_id4', readonly=False)

    document_id5 = fields.Char(related='company_id.document_id5', readonly=False)
    document_id6 = fields.Char(related='company_id.document_id6', readonly=False)
    