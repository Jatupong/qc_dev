# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _

class Wht_tax_name(models.Model):
    _inherit = 'account.tax'

    type_name = fields.Selection([('0', 'Company Withholding Tax 1% (Transportation)'),
                                  ('1', 'Company Withholding Tax 1.5% (Service)'),
                                  ('2', 'Company Withholding Tax 2% (Advertising)'),
                                  ('3', 'Company Withholding Tax 3% (Service)'),
                                  ('4', 'Company Withholding Tax 5% (Rental)'),
                                  ('5', 'Personal Withholding Tax 1% (Transportation)'),
                                  ('6', 'Personal Withholding Tax 1.5% (Service)'),
                                  ('7', 'Personal Withholding Tax 2% (Advertising)'),
                                  ('8', 'Personal Withholding Tax 3% (Service)'),
                                  ('9', 'Personal Withholding Tax 5% (Rental)'),
                                  ('10', 'Withholding Income Tax 1% (Transportation)'),
                                  ('11', 'Withholding Income Tax 1.5% (Service)'),
                                  ('12', 'Withholding Income Tax 2% (Advertising)'),
                                  ('13', 'Withholding Income Tax 3% (Service)'),
                                  ('14', 'Withholding Income Tax 5% (Rental)')])
