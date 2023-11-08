# -*- coding: utf-8 -*-

from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    reference_date = fields.Date(string="Reference Date")
    petition_number = fields.Char(string="Petition No.")