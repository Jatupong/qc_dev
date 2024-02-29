# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _

class Account_Tax(models.Model):
    _inherit = 'account.tax'

    tax_report = fields.Boolean(string="Tax Report")
