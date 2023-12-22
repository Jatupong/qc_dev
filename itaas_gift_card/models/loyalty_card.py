# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    base_points = fields.Float("Base Points")

    def create(self, vals_list):
        print('vals_list_crate_xard_first:',vals_list)
        for vals in vals_list:
            if 'partner_id' in vals and not vals['partner_id'] and 'order_id' in vals and vals['order_id']:
                sale_id = self.env['sale.order'].browse(int(vals['order_id']))
                vals['partner_id'] = sale_id.partner_id.id
        res = super().create(vals_list)
        for obj in res:
            res.update({
                'base_points': obj.program_id.gift_card_value
            })
        return res



