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

class asset_location(models.Model):
    _name = 'asset.location'

    name = fields.Char(string='Asset Location')

class asset_move(models.Model):
    _name = 'asset.move'

    name = fields.Char('Reference')
    from_location_id = fields.Many2one('asset.location','From Location')
    from_department_id = fields.Many2one('hr.department', 'From Department')
    from_employee_id = fields.Many2one('hr.employee', 'From Employee')
    # domain = "[('state', '=', 'model'), ('user_type_id', '=?', user_type_id), ('asset_type', '=', asset_type)]" / >
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    from_model_id = fields.Many2one('account.asset', string='From Category')
    type = fields.Selection([('0','Location'),('1','Department'),('2','Employee'),('3','Category')],default='0')
    transfer_value = fields.Float('มูลค่า ณ วัน Tranfer')
    to_location_id = fields.Many2one('asset.location','To Location')
    to_department_id = fields.Many2one('hr.department','To Department')
    to_employee_id = fields.Many2one('hr.employee', 'To Employee')
    to_model_id = fields.Many2one('account.asset', string='To Category')

    amount_depreciation_new = fields.Integer('อัตราค่าเสื่อมใหม่')
    amount_tranfer_new = fields.Integer('มูลค่า ณ วันที่ Tranfer')

    date = fields.Date(string='Date')
    asset_id = fields.Many2one('account.asset',string='Asset')
    # asset_name = fields.Char(related='asset_id.name')

    @api.model
    def create(self, vals):
        res = super(asset_move, self).create(vals)
        res['name'] = self.env['ir.sequence'].next_by_code('asset.move')
        return res



class account_asset(models.Model):
    _inherit = 'account.asset'


    #remove due to similar field available on v15
    # purchase_value = fields.Float(string='Purchase Value')
    # depreciated_amount = fields.Float(string='Depreciated Value', readonly=True, compute='get_depreciated_amount')
    # purchase_date = fields.Date(string='Purchase Date'), will use acquisition date


    code = fields.Char(string='Reference Code')
    barcode = fields.Char(string='Barcode', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                   states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', readonly=True,
                                   states={'draft': [('readonly', False)]})
    serial_number = fields.Char(string='Serial Number', readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Note')
    location_id = fields.Many2one('asset.location', string='Location')

    # asset_disposal_date = fields.Date(string='Disposal Date', readonly=True,
    #                                   states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    # asset_disposal_amount = fields.Float(string='Sales Amount')
    #
    default_salvage_value = fields.Float(string='Default Salvage Value')

    disposal_type = fields.Selection([('sell', 'Sell'), ('dispose', 'Write Off')], string='Disposal Type')

    asset_move_ids = fields.One2many('asset.move','asset_id',string='Asset Movement')
    sequence_id = fields.Many2one('ir.sequence',string='Asset Sequence')



    def generate_sequence(self):
        for asset in self:
            if asset.code:
                continue
            if asset.model_id and asset.model_id.sequence_id:
                asset.code = asset.model_id.sudo().sequence_id.with_context(sequence_date=asset.acquisition_date).next_by_id()

    @api.model
    def create(self, vals):
        res = super(account_asset, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        res._onchange_model_id()
        return res

    def validate(self):
        res = super(account_asset, self).validate()
        self.generate_sequence()
        return res


    #migrate from V15
    # def close_pending_move(self, disposal_date):
    #     for asset in self:
    #         print ('close_pending_move',disposal_date)
    #         unposted_depreciation_move_ids = asset.depreciation_move_ids.filtered(lambda x: x.state == 'draft' and x.date <= disposal_date)
    #         for move_id in unposted_depreciation_move_ids:
    #             move_id.post()
    #
    #
    # #if disposal date is in-between month, then create a last depreciation date till this date,#Issue Disposal
    # def create_last_move(self, disposal_date):
    #     # print ('create_last_move----')
    #     for asset in self:
    #         unposted_depreciation_move_ids = asset.depreciation_move_ids.filtered(
    #             lambda x: x.state == 'draft')
    #         # print ('unposted_depreciation_move_ids',unposted_depreciation_move_ids)
    #         if unposted_depreciation_move_ids:
    #             unposted_depreciation_move_ids[0].asset_depreciated_value -= unposted_depreciation_move_ids[0].amount_total
    #             unposted_depreciation_move_ids[0].asset_remaining_value += unposted_depreciation_move_ids[0].amount_total
    #
    #             ############ GET PER DAY FROM PER YEAR ##################
    #             number_of_year = self.model_id.method_number / 12
    #
    #             per_year_depreciation = (asset.original_value - asset.salvage_value) / number_of_year
    #             total_days = (disposal_date.year % 4) and 365 or 366
    #             # print('TOTOlday', total_days)
    #             per_day_depreciation = per_year_depreciation / total_days
    #             print('per_day_depreciation', per_day_depreciation)
    #             new_amount = per_day_depreciation * disposal_date.day
    #             ############ GET PER DAY FROM PER YEAR ##################
    #             # new_amount = (unposted_depreciation_move_ids[0].amount_total / unposted_depreciation_move_ids[0].date.day) * disposal_date.day
    #
    #             unposted_depreciation_move_ids[0].date = disposal_date
    #             unposted_depreciation_move_ids[0].amount_total = new_amount
    #             for line in unposted_depreciation_move_ids[0].line_ids:
    #                 if line.credit:
    #                     line.with_context(check_move_validity=False).credit = new_amount
    #                 else:
    #                     line.with_context(check_move_validity=False).debit = new_amount
    #
    #             unposted_depreciation_move_ids[0].asset_depreciated_value += new_amount
    #             unposted_depreciation_move_ids[0].asset_remaining_value -= new_amount
    #             unposted_depreciation_move_ids[0].auto_post = False
    #             unposted_depreciation_move_ids[0].post()
    #
    # def _get_disposal_moves(self, invoice_line_ids, disposal_date):
    #     self.close_pending_move(disposal_date)
    #     self.create_last_move(disposal_date) #create the last move for number of day before dispose
    #     res = super(account_asset,self)._get_disposal_moves(invoice_line_ids,disposal_date)
    #     return res
    #
    #
    #
    # def set_to_close(self, invoice_line_id, date=None):
    #     if invoice_line_id:
    #         self.write({'asset_disposal_amount': abs(invoice_line_id.balance)})
    #     if self.asset_disposal_date:
    #         date = self.asset_disposal_date
    #
    #
    #     return super(account_asset, self).set_to_close(invoice_line_id,date)
    #
    @api.onchange('model_id')
    def _onchange_model_id(self):
        super(account_asset, self)._onchange_model_id()
        model = self.model_id
        if model:
            self.salvage_value = model.default_salvage_value
    #
    #
    # def _compute_board_amount(self, computation_sequence, residual_amount, total_amount_to_depr, max_depreciation_nb, starting_sequence, depreciation_date):
    #     amount = 0
    #     if computation_sequence == max_depreciation_nb:
    #         # last depreciation always takes the asset residual amount
    #         amount = residual_amount
    #     else:
    #         if self.method in ('degressive', 'degressive_then_linear'):
    #             amount = residual_amount * self.method_progress_factor
    #         if self.method in ('linear', 'degressive_then_linear'):
    #             nb_depreciation = max_depreciation_nb - starting_sequence
    #             if self.prorata:
    #                 nb_depreciation -= 1
    #
    #             month_days = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
    #             if int(self.method_period) % 12 != 0: ###This is month, self.method_period =1 if self.method_period == 12, then per year.
    #                 number_of_year = self.model_id.method_number / 12
    #                 # per_year_depreciation = total_amount_to_depr / number_of_year
    #                 per_year_depreciation = (self.original_value-self.salvage_value) / number_of_year
    #                 total_days = (depreciation_date.year % 4) and 365 or 366
    #                 # print ('TOTOlday',total_days)
    #                 per_day_depreciation = per_year_depreciation / total_days
    #                 # print ('per_day_depreciation',per_day_depreciation)
    #                 amount_depreciation = per_day_depreciation * month_days
    #
    #
    #             else: # this is per year
    #                 amount_depreciation = total_amount_to_depr / nb_depreciation
    #
    #             linear_amount = min(amount_depreciation, residual_amount)
    #             print (linear_amount)
    #
    #             if self.method == 'degressive_then_linear':
    #                 amount = max(linear_amount, amount)
    #             else:
    #                 amount = linear_amount
    #     return amount

def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))


# class AssetSell(models.TransientModel):
#     _inherit = 'account.asset.sell'
#
#     def do_action(self):
#         self.asset_id.write({'disposal_type': self.action})
#         return super(AssetSell,self).do_action()