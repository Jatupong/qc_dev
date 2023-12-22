# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

import ast

from odoo import models


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    def _get_valid_partners(self, partners):
        '''
        Returns a dict containing the products that match per rule of the program
        '''
        rule_partner = dict()
        for rule in self.rule_ids:
            domain = rule._get_valid_partner_domain()
            if domain:
                rule_partner[rule] = partners.filtered_domain(domain)
            else:
                rule_partner[rule] = partners
        return rule_partner
