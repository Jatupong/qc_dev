# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
# from bahttext import bahttext
# from num2words import num2words
import locale


class ResPartner(models.Model):
    _inherit = "res.partner"

    payment_method_id = fields.Many2one('payment.method.type', string='Payment Method')
