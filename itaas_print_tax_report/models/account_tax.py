# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).
import math
from datetime import datetime
from odoo.exceptions import UserError

from odoo import api, fields, models, _

class Account_Tax(models.Model):
    _inherit = 'account.tax'

    wht_personal_company = fields.Selection([('personal', 'ภงด3'), ('company', 'ภงด53'),('pnd1_kor', 'ภงด1ก'),('pnd1_kor_special', 'ภงด1ก พิเศษ'),('pnd2', 'ภงด2'),('pnd2_kor', 'ภงด2ก'),('personal_kor', 'ภงด3ก')])
    is_tax_not_due = fields.Boolean('Tax is not due')
    is_tax_exempted = fields.Boolean('Tax is Exempted')

class account_move(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        print('kkkkkkkk')
        res = super(account_move, self).action_post()
        for move in self:
            if move.move_type in ('in_invoice','in_refund'):
                tax = move.invoice_line_ids.filtered(lambda r: r.tax_ids).mapped('tax_ids')
                account = tax.invoice_repartition_line_ids.filtered(lambda r: r.account_id and r.account_id.purchase_tax_report == False)
                tax_report = tax.filtered(lambda r: r.tax_report == False)
                if not move.ref:
                    if not account and not tax_report:
                        raise UserError(_('Please Set Reference !'))
                else:
                    for line in move.line_ids:
                        line.update({
                            'ref':move.ref,
                        })
                        print('line_last.ref:',line.ref)

        return res



class account_move_line_inherit(models.Model):
    _inherit ="account.move.line"

    tax_inv_date = fields.Date(string="Tax Inv Date", related="move_id.tax_invoice_date")
    date_vat_new = fields.Date(string="Date Vat" ,copy=False)
    ref_new = fields.Char(string="Ref" ,copy=False)
    is_special_tax = fields.Boolean(string='Special Tax',copy=False)


    account_for_vat_0 = fields.Many2one("account.account", string="Account Vat 0")


    def address_sum(self, address):

        a1 = ""
        if address.street and address.street2 and address.city and address.state_id and address.zip:
            a1 = address.street + address.street2 + address.city + address.state_id.name + address.zip
        elif address.street and address.street2 and address.city and address.state_id and not address.zip:
            a1 = address.street + address.street2 + address.city + address.state_id.name
        elif address.street and address.street2 and address.city and not address.state_id and not address.zip:
            a1 = address.street + address.street2 + address.city
        elif address.street and address.street2 and not address.city and not address.state_id and not address.zip:
            a1 = address.street + address.street2
        elif address.street and not address.street2 and not address.city and not address.state_id and not address.zip:
            a1 = address.street

        elif address.street and address.street2 and not address.city and address.state_id and address.zip:
            a1 = address.street + address.street2 + address.state_id.name + address.zip
        elif address.street and address.street2 and not address.city and address.state_id and not address.zip:
            a1 = address.street + address.street2 + address.state_id.name
        elif address.street and address.street2 and not address.city and not address.state_id and address.zip:
            a1 = address.street + address.street2 + address.zip


        elif address.street and address.street2 and address.city and not address.state_id and address.zip:
            a1 = address.street + address.street2 + address.city + address.zip
        elif address.street and address.street2 and address.city and not address.state_id and not address.zip:
            a1 = address.street + address.street2 + address.city

        elif address.street and address.street2 and address.city and address.state_id and not address.zip:
            a1 = address.street + address.street2 + address.city + address.state_id.name


        elif address.street and not address.street2 and address.city and address.state_id and address.zip:
            a1 = address.street + address.city + address.state_id.name + address.zip
        elif address.street and not address.street2 and not address.city and address.state_id and address.zip:
            a1 = address.street + address.state_id.name + address.zip
        elif address.street and not address.street2 and not address.city and not address.state_id and address.zip:
            a1 = address.street + address.zip

        print(a1)
        return a1


    def roundup_itaas(self,number):
        number = math.ceil(number)
        print(number)
        # datetime.days
        return number


    def get_date_format(self):
        vals = datetime.today().date()
        txt = str(vals).split('-')
        txt_2 = str(txt[2])
        return txt_2
    def get_date_format1(self):
        vals = datetime.today().date()
        txt = str(vals).split('-')
        txt_3 = str(txt[1])
        return txt_3
    def get_date_format2(self):
        vals = datetime.today().date()
        txt = str(vals).split('-')
        txt_4 = str(txt[0])
        return txt_4





