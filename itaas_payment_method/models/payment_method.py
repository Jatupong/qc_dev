# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
# from bahttext import bahttext
# from num2words import num2words
import locale


class payment_method_type(models.Model):
    _name = 'payment.method.type'

    name = fields.Char(string='Payment Method')
    level = fields.Integer(string='Level')