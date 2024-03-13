# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    supplier_evaluation_ids = fields.One2many('supplier.evaluation', 'partner_id', string='Evaluation')