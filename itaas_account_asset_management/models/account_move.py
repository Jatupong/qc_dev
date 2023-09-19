# -*- coding: utf-8 -*-
# by itaas.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import math
import re
from datetime import date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class AccountMove(models.Model):
    _inherit = 'account.move'

    etd = fields.Date(string='ETD')
    eta = fields.Date(string='ETA')
    export_products_id = fields.Char(string='เลขที่ใบขนสินค้าขาออก')
    customs_department = fields.Float(string='กรมศุลกากร',default=33.3188)

    is_asset_reserve = fields.Boolean(string='Asset Reserve')
    # is_check_asset = fields.Boolean(string="Check Asset")
    #
    # @api.model
    # def _prepare_move_for_asset_depreciation(self, vals):
    #     missing_fields = {'asset_id', 'move_ref', 'amount', 'asset_remaining_value', 'asset_depreciated_value'} - set(vals)
    #     if missing_fields:
    #         raise UserError(_('Some fields are missing {}').format(', '.join(missing_fields)))
    #     asset = vals['asset_id']
    #     account_analytic_id = asset.account_analytic_id
    #     analytic_tag_ids = asset.analytic_tag_ids
    #     depreciation_date = vals.get('date', fields.Date.context_today(self))
    #     company_currency = asset.company_id.currency_id
    #     current_currency = asset.currency_id
    #     prec = company_currency.decimal_places
    #     amount_currency = vals['amount']
    #     amount = current_currency._convert(amount_currency, company_currency, asset.company_id, depreciation_date)
    #     # Keep the partner on the original invoice if there is only one
    #     partner = asset.original_move_line_ids.mapped('partner_id')
    #     partner = partner[:1] if len(partner) <= 1 else self.env['res.partner']
    #     if asset.original_move_line_ids and asset.original_move_line_ids[0].move_id.move_type in ['in_refund',
    #                                                                                               'out_refund']:
    #         amount = -amount
    #         amount_currency = -amount_currency
    #     move_line_1 = {
    #         'name': asset.name,
    #         'partner_id': partner.id,
    #         'account_id': asset.account_depreciation_id.id,
    #         'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
    #         'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
    #         'analytic_account_id': account_analytic_id.id if asset.asset_type == 'sale' else False,
    #         'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
    #         'currency_id': current_currency.id,
    #         'amount_currency': -amount_currency,
    #     }
    #     move_line_2 = {
    #         'name': asset.name,
    #         'partner_id': partner.id,
    #         'account_id': asset.account_depreciation_expense_id.id,
    #         'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
    #         'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
    #         'analytic_account_id': account_analytic_id.id if asset.asset_type in ('purchase', 'expense') else False,
    #         'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type in (
    #         'purchase', 'expense') else False,
    #         'currency_id': current_currency.id,
    #         'amount_currency': amount_currency,
    #     }
    #     move_vals = {
    #         'ref': vals['move_ref'],
    #         'partner_id': partner.id,
    #         'date': depreciation_date,
    #         'journal_id': asset.journal_id.id,
    #         'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
    #         'auto_post': asset.state == 'open',
    #         'asset_id': asset.id,
    #         'asset_remaining_value': vals['asset_remaining_value'],
    #         'asset_depreciated_value': vals['asset_depreciated_value'],
    #         'amount_total': amount,
    #         'name': '/',
    #         'asset_value_change': vals.get('asset_value_change', False),
    #         'move_type': 'entry',
    #         'currency_id': current_currency.id,
    #     }
    #     return move_vals

    # def action_gennarat_value(self):
    #     print('action_gennarat_value:')
    #     aseet_move_ids = self.env['account.move'].search([('asset_id','!=',False),
    #                                                       ('is_check_asset','=',False)],limit=100)
    #
    #
    #     print('aseet_move_ids:',aseet_move_ids)
    #     print('aseet_move_ids:',len(aseet_move_ids))
    #     for aseet_move_id in aseet_move_ids:
    #         aseet_move_id.analytic_account_id = aseet_move_id.asset_id.account_analytic_id.id
    #         aseet_move_id.operating_unit_id = aseet_move_id.asset_id.sale_office_id.id
    #         aseet_move_id.is_check_asset = True
    #         for aseet_line in aseet_move_id.line_ids:
    #             aseet_line.analytic_account_id = aseet_move_id.asset_id.account_analytic_id.id
    #             # aseet_line.operating_unit_id = aseet_move_id.asset_id.sale_office_id.id




    def _auto_create_asset(self):
        for move in self:
            if move.is_asset_reserve:
                # print ('IGNORE--')
                return False
            else:
                return super(AccountMove, self)._auto_create_asset()