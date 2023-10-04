# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)


import base64
import xlwt
from io import BytesIO
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import misc
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
from datetime import datetime, timedelta, date, time

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))


class WizardAccountAgingReport(models.TransientModel):
    _name = 'wizard.account.aging.report'
    _description = 'Wizard Deposit Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    report_type = fields.Selection([('ar', 'ลูกหนี้'), ('ap', 'เจ้าหนี้')], string='Type', required=True, default='ap')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.model
    def default_get(self, fields):
        res = super(WizardAccountAgingReport, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    def print_report_pdf(self):
        [data] = self.read()
        data = {'form': data}
        if self.report_type == 'ap':
            return self.env.ref('qc_account_aging_report.account_ap_aging_report').report_action([], data=data,
                                                                                                    config=False)
        else:
            return self.env.ref('qc_account_aging_report.account_ar_aging_report').report_action([], data=data,
                                                                                                    config=False)

    def print_report_excel(self):
        [data] = self.read()
        data = {'form': data}

        if self.report_type == 'ap':
            return self.env.ref('qc_account_aging_report.account_ap_aging_report_xls').report_action([], data=data,
                                                                                                     config=False)
        else:
            return self.env.ref('qc_account_aging_report.account_ar_aging_report_xls').report_action([], data=data,
                                                                                                     config=False)

    def _get_out_invoice(self):
        domain = [('invoice_date', '>=', self.date_from),
                  ('invoice_date', '<=', self.date_to),
                  ('state', 'in', ['posted']),
                  ('move_type', 'in', ['out_invoice']),
                  ]

        return self.env['account.move'].search(domain)

    def _get_in_invoice(self):
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', ['posted']),
            ('move_type', 'in', ['in_invoice']),
        ]

        return self.env['account.move'].search(domain)

    def _get_invoice_days(self, move):
        invoice_days = (move.invoice_date - fields.Date.today()).days

        return invoice_days

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time


class WizardAccountApAgingReportXls(models.AbstractModel):
    _name = 'report.qc_account_aging_report.account_ap_aging_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print('generate_xlsx_report product_in_report_xls')
        for_left = workbook.add_format({'align': 'left'})
        for_left_border = workbook.add_format({'align': 'left', 'border': True})
        for_left_bold = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True})
        for_left_bold_border = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True, 'border': True})

        for_right = workbook.add_format({'align': 'right'})
        for_right_border = workbook.add_format({'align': 'right', 'border': True})
        for_right_bold_border = workbook.add_format({'align': 'right', 'border': True, 'bold': True})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'border': True, 'bold': True, 'num_format': '#,##0.00'})

        for_center = workbook.add_format({'align': 'center'})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True})
        for_center_border = workbook.add_format({'align': 'center', 'border': True})
        for_center_bold_border = workbook.add_format({'valign': 'vcenter','align': 'center', 'bold': True, 'border': True})
        for_center_border_num_format = workbook.add_format({'align': 'center', 'border': True, 'num_format': '#,##0.00'})

        for_center_date = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy'})
        for_center_datetime = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy HH:MM'})

        # def convert_utc_to_usertz(date_time):
        #     if not date_time:
        #         return ''
        #     user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        #     tz = pytz.timezone('UTC')
        #     date_time = tz.localize(fields.Datetime.from_string(date_time)).astimezone(user_tz)
        #     date_time = date_time.strftime('%d/%m/%Y %H:%M')
        #
        #     return date_time

        str2d = fields.Date.from_string
        str2dt = fields.Datetime.from_string
        date_from = str2d(lines.date_from)
        date_to = str2d(lines.date_to)
        date_from_time = lines.convert_usertz_to_utc(
            datetime.combine(fields.Date.from_string(lines.date_from), time.min))
        date_to_time = lines.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_to), time.max))

        invoice_ids = lines._get_in_invoice()
        if not invoice_ids:
            raise UserError(_("Document is empty."))

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 20, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'รายละเอียดเจ้าหนี้ค้างรับ', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'ณ ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row, i_col + 13, 'เจ้าหนี้การค้า', for_center_bold_border)
        i_col += 14
        worksheet.merge_range(i_row, i_col, i_row, i_col + 2, 'หักชำระเงินมัดจำ', for_center_bold_border)
        i_col += 3
        worksheet.merge_range(i_row, i_col, i_row, i_col + 3, 'หัก CREDIT NOTE', for_center_bold_border)
        i_col += 4
        worksheet.merge_range(i_row, i_col, i_row, i_col + 3, 'เจ้าหนี้สุทธิ ตามบัญชี', for_center_bold_border)
        i_col += 4
        worksheet.merge_range(i_row, i_col, i_row + 2, i_col, 'ขาด/เกินวงเงิน', for_center_bold_border)

        i_row += 1
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่รับซื้อ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ชื่อผู้ขาย', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'PI NO.', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงินตาม(PO)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'BIlls NO./\nเลขที่ใบแจ้งหนี้', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เงื่อนไข\nการชำระเงิน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ระยะเวลา\nการชำระเงิน(วัน)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วงเงินเชื่อที่\nได้รับอนุมัติ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ครบ\nกำหนด', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อายุเจ้าหนี้', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'สกุลเงิน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อัตราแลกเปลี่ยน\nแลกเปลี่ยน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ชำระ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ชำระ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เลขที่เอกสาร', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'ตามBILLS', for_center_bold_border)
        worksheet.write(i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        worksheet.write(i_row + 1, i_col + 1, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 2
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'สะสมรายลูกค้า', for_center_bold_border)
        worksheet.write(i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        worksheet.write(i_row + 1, i_col + 1, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 2
        i_row += 1
        for move in invoice_ids:
            i_col = 0
            i_row += 1
            worksheet.write(i_row, i_col, move.invoice_date or '', for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move.partner_id.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.purchase_id.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.purchase_id.amount_total or '', for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_payment_term_id.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_payment_term_id.name or '', for_left_border)
            i_col += 1
            credit_limit_amount = 0.0
            worksheet.write(i_row, i_col, credit_limit_amount, for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_date_due, for_center_date)
            i_col += 1
            invoice_days = move.invoice_date - fields.Date.today()
            worksheet.write(i_row, i_col, invoice_days, for_right_border)
            if move.company_currency_id != move.currency_id:
                i_col += 1
                worksheet.write(i_row, i_col, move.currency_id.name, for_left_border)
                i_col += 1
                currency_rate = move.company_currency_id._get_rates(move.company_id, move.invoice_date).get(move.company_currency_id.id)
                worksheet.write(i_row, i_col, currency_rate, for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, move.amount_total, for_right_border_num_format)
                i_col += 1
                amount_currency = move.currency_id._convert(move.amount_total, move.company_currency_id, move.company_id,
                                                            move.invoice_date or move.date)
                worksheet.write(i_row, i_col, amount_currency, for_right_border_num_format)
            else:
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, move.amount_total, for_right_border_num_format)
            # -
            i_col += 1
            worksheet.write(i_row, i_col, '', for_center_date)
            i_col += 1
            invoice_down_payment_amount = 0.0
            worksheet.write(i_row, i_col, invoice_down_payment_amount, for_right_border_num_format)
            i_col += 1
            invoice_down_payment_amount = 0.0
            worksheet.write(i_row, i_col, invoice_down_payment_amount, for_right_border_num_format)
            # -
            credit_note_ids = self.env['account.move'].search([('reversed_entry_id', '=', move.id)])
            if credit_note_ids:
                credit_note_id = credit_note_ids[0]
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.invoice_date, for_center_date)
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.name, for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.amount_total, for_right_border_num_format)
                i_col += 1
                amount_currency = credit_note_id.currency_id._convert(credit_note_id.amount_total, credit_note_id.company_currency_id,
                                                                      credit_note_id.company_id,
                                                                      credit_note_id.invoice_date or move.date)
                worksheet.write(i_row, i_col, amount_currency, for_right_border_num_format)
            else:
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)

            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)


        workbook.close()


class WizardAccountArAgingReportXls(models.AbstractModel):
    _name = 'report.qc_account_aging_report.account_ar_aging_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print('generate_xlsx_report product_in_report_xls')
        for_left = workbook.add_format({'align': 'left'})
        for_left_border = workbook.add_format({'align': 'left', 'border': True})
        for_left_bold = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True})
        for_left_bold_border = workbook.add_format({'valign': 'top', 'align': 'left', 'bold': True, 'border': True})

        for_right = workbook.add_format({'align': 'right'})
        for_right_border = workbook.add_format({'align': 'right', 'border': True})
        for_right_bold_border = workbook.add_format({'align': 'right', 'border': True, 'bold': True})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'border': True, 'bold': True, 'num_format': '#,##0.00'})

        for_center = workbook.add_format({'align': 'center'})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True})
        for_center_border = workbook.add_format({'align': 'center', 'border': True})
        for_center_bold_border = workbook.add_format(
            {'valign': 'vcenter', 'align': 'center', 'bold': True, 'border': True})
        for_center_border_num_format = workbook.add_format(
            {'align': 'center', 'border': True, 'num_format': '#,##0.00'})

        for_center_date = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy'})
        for_center_datetime = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy HH:MM'})

        # def convert_utc_to_usertz(date_time):
        #     if not date_time:
        #         return ''
        #     user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        #     tz = pytz.timezone('UTC')
        #     date_time = tz.localize(fields.Datetime.from_string(date_time)).astimezone(user_tz)
        #     date_time = date_time.strftime('%d/%m/%Y %H:%M')
        #
        #     return date_time

        str2d = fields.Date.from_string
        str2dt = fields.Datetime.from_string
        date_from = str2d(lines.date_from)
        date_to = str2d(lines.date_to)
        date_from_time = lines.convert_usertz_to_utc(
            datetime.combine(fields.Date.from_string(lines.date_from), time.min))
        date_to_time = lines.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_to), time.max))

        invoice_ids = lines._get_out_invoice()
        if not invoice_ids:
            raise UserError(_("Document is empty."))

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 20, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'รายละเอียดลูกหนี้ค้างรับ', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'ณ ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row, i_col + 13, 'ลูกหนี้การค้า', for_center_bold_border)
        i_col += 14
        worksheet.merge_range(i_row, i_col, i_row, i_col + 2, 'หักชำระเงินมัดจำ', for_center_bold_border)
        i_col += 3
        worksheet.merge_range(i_row, i_col, i_row, i_col + 3, 'หัก CREDIT NOTE', for_center_bold_border)
        i_col += 4
        worksheet.merge_range(i_row, i_col, i_row, i_col + 3, 'ลูกหนี้สุทธิ ตามบัญชี', for_center_bold_border)
        i_col += 4
        worksheet.merge_range(i_row, i_col, i_row + 2, i_col, 'ขาด/เกินวงเงิน', for_center_bold_border)

        i_row += 1
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ทีมขาย', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ส่งออก', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ชื่อลูกค้า', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'PI NO.', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'INVOICE NO./\nเลขที่ใบกำกับภาษี', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เงื่อนไข\nการชำระเงิน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ระยะเวลา\nการชำระเงิน(วัน)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วงเงินเชื่อที่\nได้รับอนุมัติ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ครบ\nกำหนด', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อายุเจ้าหนี้', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'สกุลเงิน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อัตราแลกเปลี่ยน\nแลกเปลี่ยน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ชำระ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่ชำระ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เลขที่เอกสาร', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'ตามINVOICE', for_center_bold_border)
        worksheet.write(i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        worksheet.write(i_row + 1, i_col + 1, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 2
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'สะสมรายลูกค้า', for_center_bold_border)
        worksheet.write(i_row + 1, i_col, 'จำนวนเงิน\n(ต่างประเทศ)', for_center_bold_border)
        worksheet.write(i_row + 1, i_col + 1, 'จำนวนเงิน\n(บาท)', for_center_bold_border)
        i_col += 2
        i_row += 1
        for move in invoice_ids:
            i_col = 0
            i_row += 1
            worksheet.write(i_row, i_col, move.team_id.name or '', for_left_border)
            i_row += 1
            worksheet.write(i_row, i_col, move.invoice_date or '', for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move.partner_id.name or '', for_left_border)
            if move.line_ids.sale_line_ids:
                i_col += 1
                sale_id = move.line_ids.sale_line_ids[0].order_id
                worksheet.write(i_row, i_col, sale_id.name or '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, sale_id.amount_total or '', for_right_border_num_format)
            else:
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_payment_term_id.name or '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_payment_term_id.name or '', for_left_border)
            i_col += 1
            credit_limit_amount = 0.0
            worksheet.write(i_row, i_col, credit_limit_amount, for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move.invoice_date_due, for_center_date)
            i_col += 1
            invoice_days = move.invoice_date - fields.Date.today()
            worksheet.write(i_row, i_col, invoice_days, for_right_border)
            if move.company_currency_id != move.currency_id:
                i_col += 1
                worksheet.write(i_row, i_col, move.currency_id.name, for_left_border)
                i_col += 1
                currency_rate = move.company_currency_id._get_rates(move.company_id, move.invoice_date).get(
                    move.company_currency_id.id)
                worksheet.write(i_row, i_col, currency_rate, for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, move.amount_total, for_right_border_num_format)
                i_col += 1
                amount_currency = move.currency_id._convert(move.amount_total, move.company_currency_id,
                                                            move.company_id,
                                                            move.invoice_date or move.date)
                worksheet.write(i_row, i_col, amount_currency, for_right_border_num_format)
            else:
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, move.amount_total, for_right_border_num_format)
            # -
            i_col += 1
            worksheet.write(i_row, i_col, '', for_center_date)
            i_col += 1
            invoice_down_payment_amount = 0.0
            worksheet.write(i_row, i_col, invoice_down_payment_amount, for_right_border_num_format)
            i_col += 1
            invoice_down_payment_amount = 0.0
            worksheet.write(i_row, i_col, invoice_down_payment_amount, for_right_border_num_format)
            # -
            credit_note_ids = self.env['account.move'].search([('reversed_entry_id', '=', move.id)])
            if credit_note_ids:
                credit_note_id = credit_note_ids[0]
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.invoice_date, for_center_date)
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.name, for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, credit_note_id.amount_total, for_right_border_num_format)
                i_col += 1
                amount_currency = credit_note_id.currency_id._convert(credit_note_id.amount_total,
                                                                      credit_note_id.company_currency_id,
                                                                      credit_note_id.company_id,
                                                                      credit_note_id.invoice_date or move.date)
                worksheet.write(i_row, i_col, amount_currency, for_right_border_num_format)
            else:
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, '', for_left_border)

            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, '', for_left_border)

        workbook.close()
