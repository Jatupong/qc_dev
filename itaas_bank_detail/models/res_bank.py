# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    fax = fields.Char(string='Fax')