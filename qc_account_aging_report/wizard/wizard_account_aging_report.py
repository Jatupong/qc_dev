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

    def _get_result_ap_aging(self):
        record = []
        invoice_ids = self._get_in_invoice()
        if not invoice_ids:
            raise UserError(_("Document is empty."))
        for move in invoice_ids:

            purchase_id = move.line_ids.purchase_line_id.order_id
            if purchase_id:
                po_no = purchase_id.name or ''
                po_amount_total = '{0:,.2f}'.format(purchase_id.amount_total)
            else:
                po_no = ''
                po_amount_total = ''

            credit_limit_amount = 0.0
            currency_name = ''
            if move.currency_id != move.company_currency_id:
                price_total = sum(move.line_ids.filtered(lambda x: not x.is_downpayment).mapped('price_total'))
                amount_other_currency = price_total
                currency_rate = move.company_currency_id._get_rates(move.company_id,
                                                                    move.invoice_date or move.date).get(
                    move.company_currency_id.id)

                amount_currency = move.currency_id._convert(price_total,
                                                            move.company_currency_id,
                                                            move.company_id,
                                                            move.invoice_date or move.date)
            else:
                amount_other_currency = 0.0
                currency_rate = ''
                amount_currency = sum(move.line_ids.filtered(lambda x: not x.is_downpayment).mapped('price_total'))

            if move.line_ids.filtered(lambda x: x.is_downpayment):
                if move.currency_id != move.company_currency_id:
                    price_total = abs(sum(move.line_ids.filtered(lambda x: x.is_downpayment).mapped('price_total')))
                    down_payment_amount_other_currency = move.currency_id._convert(price_total,
                                                                                   move.company_currency_id,
                                                                                   move.company_id,
                                                                                   move.invoice_date or move.date)
                    down_payment_date = ''
                    down_payment_amount = abs(
                        sum(move.line_ids.filtered(lambda x: x.is_downpayment).mapped('price_total')))
                else:
                    down_payment_amount_other_currency = 0.0
                    down_payment_date = ''
                    down_payment_amount = abs(
                        sum(move.line_ids.filtered(lambda x: x.is_downpayment).mapped('price_total')))
            else:
                down_payment_amount_other_currency = 0.0
                down_payment_date = ''
                down_payment_amount = 0.0

            credit_note_ids = self.env['account.move'].search([('reversed_entry_id', '=', move.id),
                                                               ('state', 'in', ['posted'])])
            if credit_note_ids:
                credit_note_id = credit_note_ids[0]
                cn_date = credit_note_id.invoice_date
                cn_no = credit_note_id.name
                if credit_note_id.currency_id != credit_note_id.company_currency_id:
                    cn_amount_other_currency = credit_note_id.amount_total
                    cn_amount = credit_note_id.currency_id._convert(credit_note_id.amount_total,
                                                                    credit_note_id.company_currency_id,
                                                                    credit_note_id.company_id,
                                                                    credit_note_id.invoice_date or move.date)
                else:
                    cn_amount_other_currency = 0.0
                    cn_amount = credit_note_id.amount_total
            else:
                cn_date = ''
                cn_no = ''
                cn_amount_other_currency = 0.0
                cn_amount = 0.0

            inv_amount_other_currency = amount_other_currency - (
                        down_payment_amount_other_currency + cn_amount_other_currency)
            inv_amount = amount_currency - (down_payment_amount + cn_amount)

            balance_amount_other_currency = 0.0
            balance_amount = 0.0

            credit_limit_note = ''

            value = {
                'invoice_date': move.invoice_date or '',
                'partner_name': move.partner_id.name or '',
                'pi_no': po_no,
                'po_amount_total': po_amount_total,
                'bill_no': move.name or '',
                'payment_term': move.invoice_payment_term_id.name or '',
                'length_payment_term': move.invoice_payment_term_id.name or '',
                'credit_limit': credit_limit_amount,
                'due_date': move.invoice_date_due.strftime('%d/%m/%Y'),
                'creditor_age': move.partner_id.use_partner_credit_limit or '',
                'currency_name': currency_name,
                'currency_rate': currency_rate,
                'amount_other_currency': '{0:,.2f}'.format(amount_other_currency),
                'amount': '{0:,.2f}'.format(amount_currency),
                'dp_date': down_payment_date,
                'dp_amount_other_currency': '{0:,.2f}'.format(down_payment_amount_other_currency),
                'dp_amount': '{0:,.2f}'.format(down_payment_amount),
                'cn_date': cn_date,
                'cn_no': cn_no,
                'cn_amount_other_currency': '{0:,.2f}'.format(cn_amount_other_currency),
                'cn_amount': '{0:,.2f}'.format(cn_amount),
                'inv_amount_other_currency': '{0:,.2f}'.format(inv_amount_other_currency),
                'inv_amount': '{0:,.2f}'.format(inv_amount),
                'balance_amount_other_currency': balance_amount_other_currency,
                'balance_amount': balance_amount,
                'credit_limit_note': credit_limit_note,
            }
            record.append(value)

        return record

    def _get_result_ar_aging(self):
        record = []
        invoice_ids = self._get_out_invoice()
        if not invoice_ids:
            raise UserError(_("Document is empty."))
        for move in invoice_ids:

            if move.line_ids.sale_line_ids:
                sale_id = move.line_ids.sale_line_ids[0].order_id
                so_no = sale_id.name
                so_amount_total = '{0:,.2f}'.format(sale_id.amount_total)
            else:
                sale_id = False
                so_no = ''
                so_amount_total = ''

            credit_limit_amount = 0.0
            currency_name = ''
            if move.currency_id != move.company_currency_id:
                price_total = sum(move.line_ids.filtered(lambda x: not x.is_downpayment).mapped('price_total'))
                amount_other_currency = price_total
                currency_rate = move.company_currency_id._get_rates(move.company_id,
                                                                    move.invoice_date or move.date).get(move.company_currency_id.id)

                amount_currency = move.currency_id._convert(price_total,
                                                            move.company_currency_id,
                                                            move.company_id,
                                                            move.invoice_date or move.date)
            else:
                amount_other_currency = 0.0
                currency_rate = ''
                amount_currency = sum(move.line_ids.filtered(lambda x: not x.is_downpayment).mapped('price_total'))

            if move.line_ids.filtered(lambda x:x.is_downpayment):
                if move.currency_id != move.company_currency_id:
                    price_total = abs(sum(move.line_ids.filtered(lambda x:x.is_downpayment).mapped('price_total')))
                    down_payment_amount_other_currency = move.currency_id._convert(price_total,
                                                                                   move.company_currency_id,
                                                                                   move.company_id,
                                                                                   move.invoice_date or move.date)
                    down_payment_date = ''
                    down_payment_amount = abs(sum(move.line_ids.filtered(lambda x:x.is_downpayment).mapped('price_total')))
                else:
                    down_payment_amount_other_currency = 0.0
                    down_payment_date = ''
                    down_payment_amount = abs(sum(move.line_ids.filtered(lambda x: x.is_downpayment).mapped('price_total')))
            else:
                down_payment_amount_other_currency = 0.0
                down_payment_date = ''
                down_payment_amount = 0.0

            credit_note_ids = self.env['account.move'].search([('reversed_entry_id', '=', move.id),
                                                               ('state', 'in', ['posted'])])
            if credit_note_ids:
                credit_note_id = credit_note_ids[0]
                cn_date = credit_note_id.invoice_date
                cn_no = credit_note_id.name
                if credit_note_id.currency_id != credit_note_id.company_currency_id:
                    cn_amount_other_currency = credit_note_id.amount_total
                    cn_amount = credit_note_id.currency_id._convert(credit_note_id.amount_total,
                                                                    credit_note_id.company_currency_id,
                                                                    credit_note_id.company_id,
                                                                    credit_note_id.invoice_date or move.date)
                else:
                    cn_amount_other_currency = 0.0
                    cn_amount = credit_note_id.amount_total
            else:
                cn_date = ''
                cn_no = ''
                cn_amount_other_currency = 0.0
                cn_amount = 0.0

            inv_amount_other_currency = amount_other_currency - (down_payment_amount_other_currency + cn_amount_other_currency)
            inv_amount = amount_currency - (down_payment_amount + cn_amount)

            balance_amount_other_currency = 0.0
            balance_amount = 0.0

            credit_limit_note = ''

            value = {
                'team_name': move.team_id.name or '',
                'invoice_date': move.invoice_date.strftime('%d/%m/%Y') or '',
                'partner_name': move.partner_id.name or '',
                'so_no': so_no,
                'so_amount_total': so_amount_total,
                'move_name': move.name or '',
                'payment_term': move.invoice_payment_term_id.name or '',
                'length_payment_term': move.invoice_payment_term_id.name or '',
                'credit_limit_amount': credit_limit_amount,
                'due_date': move.invoice_date_due.strftime('%d/%m/%Y'),
                'creditor_age': move.partner_id.use_partner_credit_limit or '',
                'currency_name': currency_name,
                'currency_rate': currency_rate,
                'amount_other_currency': '{0:,.2f}'.format(amount_other_currency),
                'amount': '{0:,.2f}'.format(amount_currency),
                'dp_date': down_payment_date,
                'dp_amount_other_currency': '{0:,.2f}'.format(down_payment_amount_other_currency),
                'dp_amount': '{0:,.2f}'.format(down_payment_amount),
                'cn_date': cn_date,
                'cn_no': cn_no,
                'cn_amount_other_currency': '{0:,.2f}'.format(cn_amount_other_currency),
                'cn_amount': '{0:,.2f}'.format(cn_amount),
                'inv_amount_other_currency': '{0:,.2f}'.format(inv_amount_other_currency),
                'inv_amount': '{0:,.2f}'.format(inv_amount),
                'balance_amount_other_currency': '{0:,.2f}'.format(balance_amount_other_currency),
                'balance_amount': '{0:,.2f}'.format(balance_amount),
                'credit_limit_note': credit_limit_note,
            }
            record.append(value)

        return record


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

        # invoice_ids = lines._get_in_invoice()
        # if not invoice_ids:
        #     raise UserError(_("Document is empty."))
        invoice_ids_list = lines._get_result_ap_aging()

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
        for move in invoice_ids_list:
            i_col = 0
            i_row += 1
            worksheet.write(i_row, i_col, move['invoice_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['partner_name'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['pi_no'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['po_amount_total'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['bill_no'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['payment_term'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['length_payment_term'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['credit_limit'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['due_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['creditor_age'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['currency_name'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['currency_rate'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_date'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_no'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['inv_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['inv_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['balance_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['balance_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['credit_limit_note'], for_left_border)

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

        # invoice_ids = lines._get_out_invoice()
        # if not invoice_ids:
        #     raise UserError(_("Document is empty."))

        invoice_list = lines._get_result_ar_aging()

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 20, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'รายละเอียดลูกหนี้ค้างรับ', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'ณ ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row, i_col + 14, 'ลูกหนี้การค้า', for_center_bold_border)
        i_col += 15
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
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงินตาม(PO)', for_center_bold_border)
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

        for move in invoice_list:
            i_col = 0
            i_row += 1
            worksheet.write(i_row, i_col, move['team_name'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['invoice_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['partner_name'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['so_no'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['so_amount_total'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['move_name'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['payment_term'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['length_payment_term'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['credit_limit_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['due_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['creditor_age'], for_right_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['currency_name'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['currency_rate'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['dp_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_date'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_no'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['cn_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['inv_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['inv_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['balance_amount_other_currency'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['balance_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['credit_limit_note'], for_left_border)

        workbook.close()
