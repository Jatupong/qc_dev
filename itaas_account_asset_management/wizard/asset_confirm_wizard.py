# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetConfirmWizard(models.TransientModel):
    _name = "asset.confirm.wizard"
    _description = "Asset Confirm Wizard"


    def action_compute(self):
        active_ids = self.env.context.get("active_ids", False)
        asset_ids = self.env['account.asset'].browse(active_ids)
        for asset_id in asset_ids:
            asset_id.compute_depreciation_board()
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", False)
        asset_ids = self.env['account.asset'].browse(active_ids)
        for asset_id in asset_ids:
            # if asset_id.temp_value_residual:
            #     asset_id.update({'value_residual':asset_id.temp_value_residual})
            asset_id.validate()
        return {'type': 'ir.actions.act_window_close'}




