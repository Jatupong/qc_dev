# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'


    coupon_date = fields.Integer("อายุคูปอง (วัน)")
    gift_card_value = fields.Float('Gift Card Value')
    valid_date = fields.Date('วันที่หมดอายุ')

    @api.onchange('coupon_date','valid_date')
    def _onchange_coupon_date(self):
        print('_onchange_coupon_date')
        for obj in self:
            if obj.coupon_date and obj.valid_date:
                raise UserError(_("Please Select อายุคูปอง(วัน) or วันที่หมดอายุ"))



