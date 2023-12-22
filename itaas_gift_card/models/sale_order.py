# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, models,fields
from odoo.tools import float_compare
import base64
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_point_changes(self):
        print('_get_point_changes_custom_for Coupom:')
        """
        Returns the changes in points per coupon as a dict.

        Used when validating/cancelling an order
        """
        points_per_coupon = defaultdict(lambda: 0)
        for coupon_point in self.coupon_point_ids:
            print('coupon_point_coupon_point')
            points_per_coupon[coupon_point.coupon_id] += coupon_point.coupon_id.program_id.gift_card_value
        for line in self.order_line:
            if not line.reward_id or not line.coupon_id:
                continue
            points_per_coupon[line.coupon_id] -= line.points_cost
            date_order = line.coupon_id.create_date.date()
            sale_obj_id = self.env['loyalty.program.line'].search([('sale_id','=',self.id)])
            if not sale_obj_id and line.coupon_id.program_id.program_type == 'gift_card' and line.coupon_id.program_id.gift_card_value :
                vals = {
                    'date_order': fields.Date.today(),
                    'date': date_order,
                    'qty': line.coupon_id.base_points,
                    'qty_done': abs(line.points_cost),
                    'ref': self.name,
                    'program_id': line.coupon_id.program_id.id,
                    'sale_id':self.id,
                    'partner_id':line.coupon_id.partner_id.id,
                }
                self.env['loyalty.program.line'].create(vals)
                line.coupon_id.base_points -= abs(line.points_cost)
        return points_per_coupon



    def action_confirm(self):
        res = super().action_confirm()
        partner_id = self.env.user.partner_id
        print('action_confirm:')
        for coupon, change in self._get_point_changes().items():
            if coupon.program_id.valid_date:
                coupon.expiration_date = coupon.program_id.valid_date
            if coupon.program_id.coupon_date:
                coupon.expiration_date = datetime.now().date() + relativedelta(days=coupon.program_id.coupon_date)
            if not coupon.partner_id:
                coupon.partner_id = partner_id.id
        return res