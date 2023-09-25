
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountAsset(models.Model):
    _inherit ='account.asset'

    @api.onchange('account_depreciation_id')
    def _onchange_account_depreciation_id(self):
        print('kkkkkk')

        asset_one = super(AccountAsset, self)._onchange_account_depreciation_id()

        if not self.original_move_line_ids:
            if self.asset_type == 'expense':
                # Always change the account since it is not visible in the form
                self.account_asset_id = self.model_id.account_asset_id
            if self.asset_type == 'purchase' and not self.account_asset_id and self.state != 'model':
                # Only set a default value since it is visible in the form
                self.account_asset_id = self.model_id.account_asset_id
        print('lllll',self.model_id.account_asset_id.name)
        return asset_one

        

    @api.onchange('account_depreciation_expense_id')
    def _onchange_account_depreciation_expense_id(self):
        print('mmmmmmm')
        
        # asset_two = super(AccountAsset, self)._onchange_account_depreciation_expense_id()
        asset_two = super()._onchange_account_depreciation_id()
        if not self.original_move_line_ids and self.asset_type not in ('purchase', 'expense'):
            print('nnnnndsdd')
        self.account_asset_id = self.model_id.account_asset_id
        return asset_two


 