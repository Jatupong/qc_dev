# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    production_order_no_form = fields.Char(string='Production Order No. Form')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    production_order_no_form = fields.Char(related='company_id.production_order_no_form', string='Production Order No. Form', readonly=False)