# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_loyalty_rule(self):
        result = super()._loader_params_loyalty_rule()
        result['search_params']['fields'].append('partner_domain')
        result['search_params']['fields'].append('valid_partner_ids')
        result['search_params']['fields'].append('any_partner')
        return result
