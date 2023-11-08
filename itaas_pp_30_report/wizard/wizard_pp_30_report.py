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


class WizardPP30Report(models.TransientModel):
    _name = 'wizard.pp.30.report'
    _description = 'Wizard PP 30 Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    journal_export_id = fields.Many2one('account.journal', string='สมุดรายวันขายต่างประเทศ', required=True)
    journal_internal_id = fields.Many2one('account.journal', string='สมุดรายวันขายในประเทศ', required=True)
    journal_shop_sale_id = fields.Many2one('account.journal', string='สมุดรายวันขายร้านค้าสวัสดิการ', required=True)

    @api.model
    def default_get(self, fields):
        res = super(WizardPP30Report, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    def print_report_excel(self):
        [data] = self.read()
        datas = {'form': data}

        str2d = fields.Date.from_string
        date_from = str2d(self.date_from)
        date_to = str2d(self.date_to)
        # date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        # date_to_obj = datetime.strptime(self.date_from, '%Y-%m-%d')
        report_file = "Stock" + str(date_from.strftime("%d/%m/%Y")) + "-" + str(date_to.strftime("%d/%m/%Y"))
        self.env.ref('itaas_pp_30_report.pp_30_report_xls').report_file = report_file

        return self.env.ref('itaas_pp_30_report.pp_30_report_xls').report_action(self, data=datas, config=False)

    def _get_results(self):
        date_from = self.date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to = self.date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # print('date_from', date_from)
        # print('date_to', date_to)

        sql_date = """
        SELECT EXTRACT(MONTH FROM aml.date) AS aml_month , EXTRACT(YEAR FROM aml.date) AS aml_year
        FROM account_move_line aml
        WHERE aml.date BETWEEN  %s AND %s
        GROUP BY aml_month, aml_year
        ORDER BY aml_month, aml_year;
        """
        self._cr.execute(sql_date, (str(date_from), str(date_to)))
        date_results = self._cr.dictfetchall()
        month_th = ['มกราคม ', 'กุมภาพันธ์ ', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                    'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
        for date in date_results:
            # print('date', date)
            date.update({'month_th': month_th[int(date['aml_month'] - 1)],})

        # print('date_results len:', len(date_results), date_results)
        sql = ("""
        SELECT EXTRACT(
        MONTH FROM aml.date) AS aml_month , 
        EXTRACT(YEAR FROM aml.date) AS aml_year,
        case when aml.journal_id = %s
             then sum(aml.price_total) end as export_amount,
        case when aml.journal_id = %s
             then sum(aml.price_total) end as internal_amount
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        WHERE am.tax_invoice_date BETWEEN %s AND %s AND am.move_type = 'out_invoice' AND am.state = 'posted'
        GROUP BY aml_month, aml_year, aml.journal_id;
        """)
        self._cr.execute(sql, (
            self.journal_export_id.id, self.journal_internal_id.id, date_from, date_to
        ))
        results = self._cr.dictfetchall()

        self._cr.execute("""
        SELECT 
        EXTRACT(MONTH FROM aml.date) AS aml_month , 
        EXTRACT(YEAR FROM aml.date) AS aml_year,
        sum(price_subtotal) AS price_subtotal
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        WHERE aml.journal_id = %s AND aml.price_subtotal != aml.price_total AND am.date BETWEEN %s AND %s AND am.state = 'posted'
        GROUP BY aml_month, aml_year;""", (
            self.journal_shop_sale_id.id, date_from, date_to))
        results_shop_sale_vat = self._cr.dictfetchall()

        self._cr.execute("""
                SELECT 
                EXTRACT(MONTH FROM aml.date) AS aml_month , 
                EXTRACT(YEAR FROM aml.date) AS aml_year,
                sum(price_subtotal) AS price_subtotal
                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                WHERE aml.journal_id = %s and aml.price_subtotal = aml.price_total and aml.date BETWEEN %s AND %s AND am.state = 'posted'
                GROUP BY aml_month, aml_year;""", (
            self.journal_shop_sale_id.id, date_from, date_to))
        results_shop_sale_no_vat = self._cr.dictfetchall()

        self._cr.execute("""
                        SELECT 
                        EXTRACT(MONTH FROM aml.date) AS aml_month , 
                        EXTRACT(YEAR FROM aml.date) AS aml_year,
                        sum(price_total) - sum(price_subtotal) AS amount_tax
                        FROM account_move_line aml
                        JOIN account_move am ON aml.move_id = am.id
                        WHERE am.tax_invoice_date BETWEEN %s AND %s AND am.move_type = 'out_invoice' AND am.state = 'posted'
                        GROUP BY aml_month, aml_year;""", (
            date_from, date_to))
        results_sale_taxes = self._cr.dictfetchall()

        self._cr.execute("""
                                SELECT 
                                EXTRACT(MONTH FROM aml.date) AS aml_month , 
                                EXTRACT(YEAR FROM aml.date) AS aml_year,
                                sum(aml.price_subtotal) AS price_subtotal,
                                sum(aml.price_total) - sum(aml.price_subtotal) AS amount_tax
                                FROM account_move_line aml
                                JOIN account_move am ON aml.move_id = am.id
                                WHERE am.tax_invoice_date BETWEEN %s AND %s AND am.move_type = 'in_invoice' AND am.state = 'posted'
                                GROUP BY aml_month, aml_year;""", (
            date_from, date_to))
        results_purchase = self._cr.dictfetchall()

        return date_results, results, results_shop_sale_vat, results_shop_sale_no_vat, results_sale_taxes, results_purchase


class WizardPP30ReportXls(models.AbstractModel):
    _name = 'report.itaas_pp_30_report.pp_30_report_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'PP 30 Report'

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time

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

        date_results, results, results_shop_sale_vat, results_shop_sale_no_vat, results_sale_taxes, results_purchase = lines._get_results()
        if not results:
            raise UserError(_("Document is empty"))

        date_from_time = self.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_from), time.min))
        date_to_time = self.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(lines.date_to), time.max))

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 8, lines.company_id.name, for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.write(i_row, i_col, 'สรุปแบบ ภพ. 30 ', for_left_bold)
        i_col += 1
        worksheet.write(i_row, i_col, 'ประจำปี', for_right)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_to)).strftime("%Y"), for_left)
        i_col = 0
        i_row += 1
        i_col += 2
        worksheet.write(i_row, i_col, strToDate(str(lines.date_from)).strftime("%d/%m/%Y"), for_left)
        i_col += 1
        worksheet.write(i_row, i_col, '-', for_center)
        i_col += 1
        worksheet.write(i_row, i_col, strToDate(str(lines.date_to)).strftime("%d/%m/%Y"), for_left)

        i_row += 2
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เดือน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ยอดส่งออก', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ขายในประเทศ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'Supplier Invoice', for_center_bold_border)
        worksheet.write(i_row + 1, i_col, 'Vat', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row + 1, i_col, 'No Vat', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'รวมรายได้', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ภาษีขาย', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'รวมขายทั้งหมด', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ยอดซื้อ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ภาษีซื้อ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ยอดรับคืนภาษี', for_center_bold_border)
        i_row += 1

        for date in date_results:
            result_by_date = list(filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results))
            results_shop_sale_vat_by_date = list(filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results_shop_sale_vat))
            results_shop_sale_no_vat_by_date = list(filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results_shop_sale_no_vat))
            results_sale_taxes_by_date = list(filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results_sale_taxes))
            results_purchase_by_date = list(filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results_purchase))
            export_amount = 0.0
            internal_amount = 0.0
            shop_sale_vat_amount = 0.0
            shop_sale_no_vat_amount = 0.0
            sale_taxes_amount = 0.0
            purchase_taxes_amount = 0.0
            purchase_amount = 0.0

            for res in result_by_date:
                export_amount += res['export_amount'] or 0.0
                internal_amount += res['internal_amount'] or 0.0
            for res in results_shop_sale_vat_by_date:
                shop_sale_vat_amount += res['price_subtotal'] or 0.0
            for res in results_shop_sale_no_vat_by_date:
                shop_sale_no_vat_amount += res['price_subtotal'] or 0.0
            for res in results_sale_taxes_by_date:
                sale_taxes_amount += res['amount_tax'] or 0.0
            for res in results_purchase_by_date:
                purchase_amount += res['price_subtotal'] or 0.0
                purchase_taxes_amount += res['amount_tax'] or 0.0

            income_amount = export_amount + internal_amount + shop_sale_vat_amount + shop_sale_no_vat_amount
            sale_amount = export_amount + internal_amount
            return_vat_amount = purchase_taxes_amount - sale_taxes_amount

            i_row += 1
            i_col = 0
            worksheet.write(i_row, i_col, date['month_th'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, export_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, internal_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, shop_sale_vat_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, shop_sale_no_vat_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, income_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, sale_taxes_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, sale_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, purchase_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, purchase_taxes_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, return_vat_amount, for_right_border_num_format)

        workbook.close()