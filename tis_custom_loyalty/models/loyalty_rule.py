# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

import ast

from odoo import fields, models


class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    partner_domain = fields.Char(default="[]", string="Partner Domain")
    valid_partner_ids = fields.Many2many(
        'res.partner', "Valid Partners", compute='_compute_valid_partner_ids',
        help="These are the partner that are valid for this rule.")
    any_partner = fields.Boolean(
        compute='_compute_valid_partner_ids', help="Technical field, whether all partner match")

    def _compute_valid_partner_ids(self):
        for rule in self:
            if rule.partner_domain not in ('[]', "[['sale_ok', '=', True]]"):
                domain = rule._get_valid_partner_domain()
                print("_get_valid_partner_domain", domain)
                rule.valid_partner_ids = self.env['res.partner'].search(domain)
                rule.any_partner = False
            else:
                rule.any_partner = True
                rule.valid_partner_ids = self.env['res.partner']

    def _get_valid_products(self):
        self.ensure_one()
        return self.env['product.product'].search(self._get_valid_partner_domain())

    def _get_valid_partner_domain(self):
        self.ensure_one()
        domain = []
        if self.partner_domain and self.partner_domain != '[]':
            domain = ast.literal_eval(self.partner_domain)
        return domain
