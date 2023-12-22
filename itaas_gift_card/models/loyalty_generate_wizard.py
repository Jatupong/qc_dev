# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

class LoyaltyGenerateWizard(models.TransientModel):
    _inherit = 'loyalty.generate.wizard'
    _description = 'Generate Coupons'



    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'params' in self._context:
            params_id = self._context['params']['id']
            model_id = self._context['params']['model']
            loyalty_id = self.env[model_id].browse(params_id)
            if loyalty_id and loyalty_id.gift_card_value:
                res['points_granted'] = loyalty_id.gift_card_value
            if loyalty_id and loyalty_id.valid_date:
                res['valid_until'] = loyalty_id.valid_date

            if loyalty_id and loyalty_id.coupon_date:
                date = datetime.now().date() + relativedelta(days=loyalty_id.coupon_date)
                res['valid_until'] = date
        return res

