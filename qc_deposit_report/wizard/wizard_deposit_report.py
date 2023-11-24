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


class WizardDepositReport(models.TransientModel):
    _name = 'wizard.deposit.report'
    _description = 'Wizard Deposit Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    partner_ids = fields.Many2many('res.partner', 'partner_deposit_ref', string='Partners')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.model
    def default_get(self, fields):
        res = super(WizardDepositReport, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    def print_report_pdf(self):
        [data] = self.read()
        data = {'form': data}

        return self.env.ref('qc_deposit_report.deposit_report').report_action([], data=data,
                                                                              config=False)

    def print_report_excel(self):
        [data] = self.read()
        datas = {'form': data}

        str2d = fields.Date.from_string
        date_from = str2d(self.date_from)
        date_to = str2d(self.date_to)
        # date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        # date_to_obj = datetime.strptime(self.date_from, '%Y-%m-%d')
        report_file = "deposit" + str(date_from.strftime("%d/%m/%Y")) + "-" + str(date_to.strftime("%d/%m/%Y"))
        self.env.ref('qc_deposit_report.deposit_report_xls').report_file = report_file

        return self.env.ref('qc_deposit_report.deposit_report_xls').report_action(self, data=datas, config=False)

    def _get_is_downpayment(self, date_from_time, date_to_time):
        domain = [('is_downpayment', '=', True),
                  ('state', 'in', ['sale', 'done']),
                  # ('order_id.date_order', '<=', date_from_time),
                  # ('order_id.date_order', '>=', date_to_time)
        ]

        if self.partner_ids:
            domain += [('partner_id', '=', self.partner_ids.ids)]

        return self.env['sale.order.line'].search(domain).mapped('order_id')

    def _get_invoice(self, date_from_time, date_to_time):
        return self._get_is_downpayment(date_from_time, date_to_time)
        # domain = [('invoice_date', '<=', self.date_from),
        #           ('invoice_date', '>=', self.date_to)]
        #
        # if self.partner_ids:
        #     domain += [('partner_id', '=', self.partner_ids.ids)]
        #
        # return self.env['account.move'].search(domain)

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time


class WizardDepositReportXls(models.AbstractModel):
    _name = 'report.qc_deposit_report.deposit_report_xls'
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

        # invoice_ids = lines._get_invoice(date_from_time, date_to_time)
        # partner_ids = invoice_ids.mapped('partner_id')

        sale_order_ids = lines._get_is_downpayment(date_from_time, date_to_time)
        if not sale_order_ids:
            raise UserError(_("Document is empty."))
        partner_ids = sale_order_ids.mapped('partner_id')

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 8, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 8, 'รายละเอียดเงินมัดจำลูกหนี้', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 8, 'ณ ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.write(i_row, i_col, 'From Date', for_left_bold)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_from)).strftime("%d/%m/%Y"), for_left)
        i_col += 1
        worksheet.write(i_row, i_col, '-', for_center)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_to)).strftime("%d/%m/%Y"), for_left)

        for partner in partner_ids:
            i_row += 2
            i_col = 0
            worksheet.merge_range(i_row, i_col, i_row, 16, partner.name, for_center_bold_border)

            i_row += 1
            i_col = 0
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'วันที่รับเงิน', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ทีมขาย', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'PI.NO', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เลขที่เอกสาร', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน \n ตาม PI', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เงื่อนไข', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'สกุลเงิน', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน(ตปท)', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'Ex.Rate', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'จำนวนเงิน(บาท)', for_center_bold_border)
            i_col += 1
            worksheet.write(i_row, i_col, 'ค่าธรรมเนียม', for_center_bold_border)
            worksheet.write(i_row + 1, i_col, '(ตปท)', for_center_bold_border)
            i_col += 1
            worksheet.write(i_row, i_col, 'รับจริง', for_center_bold_border)
            worksheet.write(i_row + 1, i_col, '(ตปท)', for_center_bold_border)
            i_col += 1
            # worksheet.write(i_row, i_col, 'จำนวนเงินที่หัก', for_center_bold_border)
            worksheet.merge_range(i_row, i_col, i_row, i_col+1, 'จำนวนเงินที่หักมัดจำ', for_center_bold_border)
            worksheet.write(i_row + 1, i_col, '(ตปท)', for_center_bold_border)
            i_col += 1
            # worksheet.write(i_row, i_col, 'มัดจำ', for_center_bold_border)
            worksheet.write(i_row + 1, i_col, '(บาท)', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'คงเหลือ', for_center_bold_border)
            worksheet.write(i_row + 1, i_col, '(ตปท)', for_center_bold_border)
            i_col += 1
            worksheet.write(i_row + 1, i_col, '(บาท)', for_center_bold_border)
            i_col += 1
            worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'Note', for_center_bold_border)

            i_row += 1
            sale_order_ids_by_partner = sale_order_ids.filtered(lambda x: x.partner_id.id == partner.id)

            for sale in sale_order_ids_by_partner.filtered(lambda x: x.name).sorted(key=lambda a: a.name):

                chack_sale_name = []
                sum_inv_amount_total = 0.0
                sum_inv_amount_total_out = 0.0
                sum1 = 0.0
                sum2 = 0.0
                for inv in sale.invoice_ids.filtered(lambda x: x.name).sorted().sorted(key=lambda a: a.name):
                    sum_inv_amount_total += inv.amount_total
                    sum_inv_amount_total_out += inv.amount_total

                for inv in sale.invoice_ids.filtered(lambda x: x.name).sorted().sorted(key=lambda a: a.name):
                    if inv.state == 'posted':
                        payment_name = []
                        label = []
                        for i in inv.invoice_line_ids:
                            payment_name.append(i.product_id.name)
                            payment_name.append(i.name)
                        print(inv.name)



                        if 'Down payment' in payment_name:
                            i_row += 1
                            i_col = 0
                            worksheet.write(i_row, i_col, inv.invoice_date, for_center_date)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv.team_id.name or '', for_left_border)
                            i_col += 1
                            worksheet.write(i_row, i_col, sale.name or '', for_left_border)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv.name or '', for_left_border)

                            sale_amount_total = False
                            invoice_payment_term_name = False
                            currency_id_name = False
                            inv_amount_total = False
                            currency_rate = False
                            inv_amount_total_THB = 0
                            fee_amount = 0
                            inv_amount_total_out = 0
                            if not (sale.name in chack_sale_name):
                                sale_amount_total = sale.amount_total
                                invoice_payment_term_name = inv.invoice_payment_term_id.name
                                if inv.company_id.currency_id != inv.currency_id:
                                    currency_id_name = inv.currency_id.name
                                    inv_amount_total = sum_inv_amount_total
                                    currency_rate = inv.currency_id.rate_ids[0].inverse_company_rate or 1.0
                                    # currency_rate = inv.company_currency_id._get_rates(inv.company_id, inv.invoice_date).get(
                                    #     inv.company_currency_id.id)
                                    inv_amount_total_THB = sale_amount_total * currency_rate
                                    fee_amount = 0.0
                                    inv_amount_total_out = sum_inv_amount_total_out
                                chack_sale_name = []

                            i_col += 1
                            worksheet.write(i_row, i_col, sale_amount_total or '', for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, invoice_payment_term_name or '', for_left_border)

                            i_col += 1
                            worksheet.write(i_row, i_col, currency_id_name or '', for_left_border)
                            # จำนวนเงิน(ตปท)
                            i_col += 1
                            worksheet.write(i_row, i_col, sale_amount_total or '', for_right_border_num_format)
                            # Ex.Rate
                            i_col += 1
                            worksheet.write(i_row, i_col, currency_rate or '', for_right_border_num_format)
                            # จำนวนเงิน(บาท)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv_amount_total_THB or '', for_right_border_num_format)
                            # ค่าธรรมเนียม
                            i_col += 1
                            worksheet.write(i_row, i_col, fee_amount or '', for_right_border_num_format)
                            # # รับจริง
                            # i_col += 1
                            # worksheet.write(i_row, i_col, inv_amount_total_out or '', for_right_border_num_format)

                            i_col += 1
                            worksheet.write(i_row, i_col, inv.amount_total or '', for_right_border_num_format)
                            # จำนวนเงินที่หัก
                            i_col += 1
                            worksheet.write(i_row, i_col,0.0, for_right_border_num_format)
                            # มัดจำ
                            i_col += 1
                            worksheet.write(i_row, i_col, 0.0, for_right_border_num_format)
                            # คงเหลือ
                            i_col += 1
                            sum1 = sum1 + inv.amount_total
                            worksheet.write(i_row, i_col, sum1, for_right_border_num_format)
                            i_col += 1
                            sum2 = (sum2 + inv.amount_total) * currency_rate
                            worksheet.write(i_row, i_col, sum2, for_right_border_num_format)
                            i_col += 1
                            if inv.narration != False:
                                note = str(inv.narration).split("<p>")
                                note = str(note[1]).split("</p>")
                                worksheet.write(i_row, i_col, note[1], for_left_border)
                            if inv.narration == False:
                                print(inv.narration)
                                worksheet.write(i_row, i_col, inv.narration or '', for_left_border)

                            chack_sale_name.append(sale.name)

                        if 'Down payment' in label:
                            i_row += 1
                            i_col = 0
                            worksheet.write(i_row, i_col, inv.invoice_date, for_center_date)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv.team_id.name or '', for_left_border)
                            i_col += 1
                            worksheet.write(i_row, i_col, sale.name or '', for_left_border)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv.name or '', for_left_border)

                            sale_amount_total = False
                            invoice_payment_term_name = False
                            currency_id_name = False
                            inv_amount_total = False
                            currency_rate = False
                            inv_amount_total_THB = 0
                            fee_amount = 0
                            inv_amount_total_out = 0
                            if not (sale.name in chack_sale_name):
                                sale_amount_total = sale.amount_total
                                invoice_payment_term_name = inv.invoice_payment_term_id.name
                                if inv.company_id.currency_id != inv.currency_id:
                                    currency_id_name = inv.currency_id.name
                                    inv_amount_total = sum_inv_amount_total
                                    currency_rate = inv.currency_id.rate_ids[0].inverse_company_rate or 1.0
                                    # currency_rate = inv.company_currency_id._get_rates(inv.company_id, inv.invoice_date).get(
                                    #     inv.company_currency_id.id)
                                    inv_amount_total_THB = sale_amount_total * currency_rate
                                    fee_amount = 0.0
                                    inv_amount_total_out = sum_inv_amount_total_out
                                chack_sale_name = []

                            i_col += 1
                            worksheet.write(i_row, i_col, sale_amount_total or '', for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, invoice_payment_term_name or '', for_left_border)

                            i_col += 1
                            worksheet.write(i_row, i_col, currency_id_name or '', for_left_border)
                            # จำนวนเงิน(ตปท)
                            i_col += 1
                            worksheet.write(i_row, i_col, sale_amount_total or '', for_right_border_num_format)
                            # Ex.Rate
                            i_col += 1
                            worksheet.write(i_row, i_col, currency_rate or '', for_right_border_num_format)
                            # จำนวนเงิน(บาท)
                            i_col += 1
                            worksheet.write(i_row, i_col, inv_amount_total_THB or '', for_right_border_num_format)
                            # ค่าธรรมเนียม
                            i_col += 1
                            worksheet.write(i_row, i_col, fee_amount or '', for_right_border_num_format)
                            # # รับจริง
                            # i_col += 1
                            # worksheet.write(i_row, i_col, inv_amount_total_out or '', for_right_border_num_format)

                            i_col += 1
                            worksheet.write(i_row, i_col,0, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sum1, for_right_border_num_format)
                            i_col += 1
                            worksheet.write(i_row, i_col, sum2, for_right_border_num_format)

                            i_col += 1
                            sum1 = sum1 - sum1
                            worksheet.write(i_row, i_col, sum1, for_right_border_num_format)
                            i_col += 1
                            sum2 = sum2 - sum2
                            worksheet.write(i_row, i_col, sum2, for_right_border_num_format)



                        # note
                            i_col += 1
                            if inv.narration !=False:
                                note = str(inv.narration).split("<p>")
                                note = str(note[1]).split("</p>")
                                worksheet.write(i_row, i_col, note[1], for_left_border)
                            if inv.narration == False:
                                print(inv.narration)
                                worksheet.write(i_row, i_col, inv.narration or '', for_left_border)

                            chack_sale_name.append(sale.name)

        workbook.close()