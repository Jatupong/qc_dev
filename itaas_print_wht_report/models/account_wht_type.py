# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _

class account_wht_type(models.Model):
    _inherit = 'account.wht.type'

    report_type = fields.Selection([('personal', 'ภงด3'), ('pnd2', 'ภงด2'), ('company', 'ภงด53')], string='Report Type')