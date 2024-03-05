# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class account_move_amount_for_reverse(models.Model):
    _inherit ="account.move"

    amount_for_reverse = fields.Float('Amount For Reverse',copy=False)


class account_invoice_wizard(models.TransientModel):
    _name ="account.invoice.wizard"

    date = fields.Date(string='Date',default=fields.datetime.today().date())
    # month = fields.Selection([(1, 'มกราคม'), (2, 'กุมภาพันธ์'), (3, 'มีนาคม'), (4, 'เมษายน'),
    #                           (5, 'พฤษภาคม'), (6, 'มิถุนายน'), (7, 'กรกฏาคม'), (8, 'สิงหาคม'),
    #                           (9, 'กันยายน'), (10, 'ตุลาคม'), (11, 'พฤศจิกายน'), (12, 'ธันวาคม'), ]
    #                          , string='Month', required=True)
    # month = fields.Selection([
    #     ('1', 'มกราคม'), ('2', 'กุมภาพันธ์'), ('3', 'มีนาคม'), ('4', 'เมษายน'),
    #     ('5', 'พฤษภาคม'), ('6', 'มิถุนายน'), ('7', 'กรกฏาคม'), ('8', 'สิงหาคม'),
    #     ('9', 'กันยายน'), ('10', 'ตุลาคม'), ('11', 'พฤศจิกายน'), ('12', 'ธันวาคม'),
    # ], string='Month', required=True)
    amount = fields.Float(string='Amount Untaxed')
    tax_amount = fields.Float(string='Tax Amount')
    is_include_vat = fields.Boolean(string='Price Include VAT')
    tax_inv_number = fields.Char(string='Tax Invoice Number')
    year = fields.Char(string='ปี', required=True)

    @api.model
    def default_get(self, fields):
        res = super(account_invoice_wizard, self).default_get(fields)
        invoice_id = self.env['account.move'].browse(self._context.get('active_ids'))[0]
        amount_tax = invoice_id.amount_tax
        amount_untaxed = invoice_id.amount_untaxed
        res.update({'tax_amount': amount_tax})
        res.update({'amount': amount_untaxed})
        curr_date = datetime.now()
        year = str(curr_date.year)
        res.update({'year': year})
        return res



    def action_generate(self):
        print('action_generate')
        invoice_id = self.env['account.move'].browse(self._context.get('active_ids'))[0]
        print('invoice_id:',invoice_id)
        gen_date = self.date
        print('invoice_id.amount_for_reverse:',invoice_id.amount_for_reverse)
        print('invoice_id.amount_tax:',invoice_id.amount_tax)
        if invoice_id.amount_for_reverse < invoice_id.amount_tax:
            if self.amount:
                invoice_id.amount_for_reverse += self.tax_amount
                invoice_id.with_context(date=gen_date).create_reverse_tax_partial(self.amount,self.tax_amount,self.tax_inv_number,self.date)
            else:
                raise UserError('กรุณาใส่ข้อมูลเพื่อกลับรายการภาษี')
            if invoice_id.adjust_move_id:
                for line in invoice_id.adjust_move_id.line_ids:
                    line.update({'partner_id': invoice_id.partner_id.id})
            if round(invoice_id.amount_for_reverse,2) > invoice_id.amount_tax:
                raise UserError('รายการกลับภาษีเกิน')

        else:
            raise UserError('รายการภาษีกลับรายการครบแล้ว')











