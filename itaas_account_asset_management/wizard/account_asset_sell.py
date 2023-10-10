# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAssetSell(models.TransientModel):
    _inherit = "account.asset.sell"

    asset_disposal_date = fields.Date(string='Disposal Date')

    def do_action(self):
        self.asset_id.update({'asset_disposal_date': self.asset_disposal_date})
        return super(AccountAssetSell,self).do_action()


