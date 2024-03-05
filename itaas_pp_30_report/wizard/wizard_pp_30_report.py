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
    year = fields.Char(string='ประจำปี', required=True)
    month_from = fields.Selection([('1', 'มกราคม'), ('2', 'กุมภาพันธ์'), ('3', 'มีนาคม'), ('4', 'เมษายน'),
                                   ('5', 'พฤษภาคม'), ('6', 'มิถุนายน'), ('7', 'กรกฏาคม'), ('8', 'สิงหาคม'),
                                   ('9', 'กันยายน'), ('10', 'ตุลาคม'), ('11', 'พฤศจิกายน'), ('12', 'ธันวาคม'), ]
                                  , string='จากเดือน', required=True)
    month_to = fields.Selection([('1', 'มกราคม'), ('2', 'กุมภาพันธ์'), ('3', 'มีนาคม'), ('4', 'เมษายน'),
                                 ('5', 'พฤษภาคม'), ('6', 'มิถุนายน'), ('7', 'กรกฏาคม'), ('8', 'สิงหาคม'),
                                 ('9', 'กันยายน'), ('10', 'ตุลาคม'), ('11', 'พฤศจิกายน'), ('12', 'ธันวาคม'), ]
                                , string='ถึงเดือน', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    journal_export_id = fields.Many2one('account.journal', string='สมุดรายวันขายต่างประเทศ', required=True)
    journal_internal_id = fields.Many2one('account.journal', string='สมุดรายวันขายในประเทศ', required=True)
    journal_shop_sale_id = fields.Many2one('account.journal', string='สมุดรายวันขายร้านค้าสวัสดิการ', required=True)

    @api.model
    def default_get(self, fields):
        res = super(WizardPP30Report, self).default_get(fields)
        curr_date = datetime.now()
        year = curr_date.year
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year + 1, 1, 1).date() - timedelta(days=1) or False
        res.update({'date_from': str(from_date),
                    'date_to': str(to_date),
                    'month_from': '1',
                    'month_to': '12',
                    'year': str(year + 543)})

        return res

    @api.onchange('year', 'month_from', 'month_to')
    def onchange_year(self):
        try:
            year_int = int(self.year)
        except ValueError:
            raise UserError(_('Please Check Year!'))

        year = int(self.year) - 543
        month_from = int(self.month_from)
        month_to = int(self.month_to)

        if month_to < month_from:
            raise UserError(_('Please Check Month!'))

        self.date_from = datetime(year, month_from, 1).date()
        if month_to == 12:
            date_to = datetime(year, 12, 31).date()
        else:
            date_to = datetime(year, month_to + 1, 1).date() - timedelta(days=1)
        self.date_to = date_to

    def print_report_pdf(self):
        [data] = self.read()
        data = {'form': data}
        return self.env.ref('itaas_pp_30_report.pp_30_report').report_action([], data=data, config=False)

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

        month_th = ['มกราคม ', 'กุมภาพันธ์ ', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                    'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
        # sql_date = """
        # SELECT EXTRACT(MONTH FROM aml.date) AS aml_month , EXTRACT(YEAR FROM aml.date) AS aml_year
        # FROM account_move_line aml
        # WHERE aml.date BETWEEN  %s AND %s
        # GROUP BY aml_month, aml_year
        # ORDER BY aml_month, aml_year;
        # """
        # self._cr.execute(sql_date, (str(date_from), str(date_to)))
        # date_results = self._cr.dictfetchall()
        # for date in date_results:
        #     date.update({'month_th': month_th[int(date['aml_month'] - 1)],})

        date_ranges = []

        # Assuming self.date_from and self.date_to are defined somewhere in your code
        if self.date_to:
            year = self.date_to.year

            for month in range(1, 13):
                first_day_of_month = datetime(year, month, 1)
                last_day_of_month = (first_day_of_month + relativedelta(day=31)).date()

                # Check if the generated date range overlaps with the input date range
                if first_day_of_month.date() <= self.date_to <= last_day_of_month:
                    last_day_of_month = self.date_to

                date_ranges.append({
                    'date_from': first_day_of_month.date(),
                    'date_to': last_day_of_month
                })

                if month >= self.date_to.month:
                    break

            print('date_ranges:', date_ranges)
        else:
            # If date_to is not provided, set it equal to date_from
            self.date_to = self.date_from
            date_ranges.append({
                'date_from': self.date_from,
                'date_to': self.date_to
            })
            print('date_ranges:', date_ranges)

        date_results = []

        for i in range(12):
            date_results.append({'aml_month': i + 1,
                                 'aml_year': self.date_to.year,
                                 'month_th': month_th[i]
                                 })

        print('date_results len:', len(date_results), date_results)

        #     case when aml.journal_id = %s
        #     then sum(aml.credit) + sum(aml.debit) end as export_amount,
        # case when aml.journal_id = %s
        # then sum(aml.credit) + sum(aml.debit) end as internal_amount
        sql = ("""
        SELECT EXTRACT(MONTH FROM am.tax_invoice_date) AS aml_month , 
        EXTRACT(YEAR FROM am.tax_invoice_date) AS aml_year, 
		case when aml.journal_id = %s 
             then sum(aml.price_subtotal) end as export_amount,
        case when aml.journal_id = %s
             then sum(aml.price_subtotal) end as internal_amount
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        WHERE am.tax_invoice_date BETWEEN %s AND %s AND am.move_type = 'out_invoice'
        GROUP BY am.tax_invoice_date, aml.journal_id;
        """)
        self._cr.execute(sql, (
            self.journal_export_id.id, self.journal_internal_id.id, date_from, date_to
        ))
        results = self._cr.dictfetchall()

        self._cr.execute("""
        SELECT 
        EXTRACT(MONTH FROM aml.date) AS aml_month , 
        EXTRACT(YEAR FROM aml.date) AS aml_year,
        sum(aml.credit) + sum(aml.debit) AS price_subtotal
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
                sum(aml.credit) + sum(aml.debit) AS price_subtotal
                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                WHERE aml.journal_id = %s and aml.price_subtotal = aml.price_total and aml.date BETWEEN %s AND %s AND am.state = 'posted'
                GROUP BY aml_month, aml_year;""", (
            self.journal_shop_sale_id.id, date_from, date_to))
        results_shop_sale_no_vat = self._cr.dictfetchall()

        self._cr.execute("""
                        SELECT 
                        EXTRACT(MONTH FROM am.tax_invoice_date) AS aml_month , 
                        EXTRACT(YEAR FROM am.tax_invoice_date) AS aml_year,
                        case when aml.display_type = 'product' 
                             then sum(aml.credit) + sum(aml.debit) end as price_subtotal,
                        case when aml.display_type = 'tax' 
                                     then sum(aml.credit) + sum(aml.debit) end as amount_tax
                        FROM account_move_line aml
                        JOIN account_move am ON aml.move_id = am.id
                        WHERE am.tax_invoice_date BETWEEN %s AND %s AND am.move_type = 'out_invoice' AND am.state = 'posted'
                        GROUP BY aml_month, aml_year, aml.display_type;""", (
            date_from, date_to))
        results_sale_taxes = self._cr.dictfetchall()

        # self._cr.execute("""
        #     SELECT
        #         EXTRACT(MONTH FROM am.tax_invoice_date) AS aml_month ,
        #         EXTRACT(YEAR FROM am.tax_invoice_date) AS aml_year,
        #         case when aml.display_type = 'product'
        #                      then sum(aml.credit) + sum(aml.debit) end as price_subtotal,
        #         case when aml.display_type = 'tax'
        #                      then sum(aml.credit) + sum(aml.debit) end as amount_tax
        #         FROM account_move_line aml
        #         JOIN account_move am ON aml.move_id = am.id
        #         WHERE am.tax_invoice_date BETWEEN %s AND %s AND
        #         am.move_type = 'in_invoice' AND am.state = 'posted' AND aml.display_type in ('product','tax')
        #         GROUP BY aml_month, aml_year, aml.display_type;""", (
        #     date_from, date_to))
        # results_purchase = self._cr.dictfetchall()

        # print('results_purchase_TESTTTTTTTTTTTTTT', results_purchase)

        results_purchase = []

        if date_ranges:
            for index, mount in enumerate(date_ranges):
                data = {'date_from': mount['date_from'], 'date_to': mount['date_to'], 'report_type': 'purchase',
                        'tax_id': False,
                        'company_id': self.company_id}
                docs = self.env['report.itaas_print_tax_report.purchase_tax_report_id']._get_report_values(self,
                                                                                                           data=data)

                amount_total_7_0 = amount_total_tax = 0

                for move_id in docs['docs']:
                    print('move_id_purchase_line:', move_id)
                    if move_id['type'] == 'in_refund':
                        if move_id['debit']:
                            amount_total_tax += move_id['debit'] * (-1)
                        else:
                            amount_total_tax += move_id['credit'] * (-1)
                        print('==============REFUND==========')
                        print('debit:', move_id['debit'])
                        print('debit:', move_id['credit'])
                        print('amount_total_tax_refund', amount_total_tax)
                        if move_id['amount_untaxed']:
                            amount_total_7_0 += move_id['amount_untaxed']
                        else:
                            if move_id['debit']:
                                amount_total_7_0 += (move_id['debit'] / 0.07)
                            elif move_id['credit']:
                                amount_total_7_0 += (move_id['credit'] / 0.07)
                    else:

                        if move_id['debit']:
                            amount_total_tax += move_id['debit']
                        else:
                            amount_total_tax += move_id['credit']
                        print('==============+NO REFUND==========')
                        print('debit:', move_id['debit'])
                        print('debit:', move_id['credit'])
                        print('amount_total_tax_no_refund', amount_total_tax)
                        if move_id['amount_untaxed']:
                            amount_total_7_0 += move_id['amount_untaxed']
                        else:
                            if move_id['debit']:
                                amount_total_7_0 += move_line_id(move_id['debit'] / 0.07)
                            elif move_id['credit']:
                                amount_total_7_0 += (move_id['credit'] / 0.07)

                data_purchase = {
                    'aml_month': index + 1,
                    'aml_year': self.date_to.year,
                    'price_subtotal': amount_total_7_0,
                    'amount_tax': amount_total_tax,
                }

                results_purchase.append(data_purchase)

                # print('data_purchaseeeeeeeeeeee', data_purchase)
                # print('docsssssssssssss'+str(index+1),docs)
                # print('mounttttttttt'+str(index+1),mount)

            # print('results_purchaseeeeeeeeeeeee', results_purchase)

        return date_results, results, results_shop_sale_vat, results_shop_sale_no_vat, results_sale_taxes, results_purchase

    def _get_result_report(self):
        record = []
        date_results, results, results_shop_sale_vat, results_shop_sale_no_vat, results_sale_taxes, results_purchase = self._get_results()
        if not results:
            raise UserError(_("Document is empty"))

        print('DATA_RESULTSSSSSSSSSSSSSSSSSSSs', date_results)

        for date in date_results:
            result_by_date = list(
                filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'], results))
            results_shop_sale_vat_by_date = list(
                filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'],
                       results_shop_sale_vat))
            results_shop_sale_no_vat_by_date = list(
                filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'],
                       results_shop_sale_no_vat))
            results_sale_taxes_by_date = list(
                filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'],
                       results_sale_taxes))
            results_purchase_by_date = list(
                filter(lambda x: x['aml_month'] == date['aml_month'] and x['aml_year'] == date['aml_year'],
                       results_purchase))

            print('results_purchase_by_dateeeeeeeeeeeeeeeee', results_purchase_by_date)
            print('result_by_dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', result_by_date)
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
                print('RESSSSSSSSSSSSSSs', res)
                purchase_amount += res['price_subtotal'] or 0.0
                purchase_taxes_amount += res['amount_tax'] or 0.0

            income_amount = export_amount + internal_amount + shop_sale_vat_amount + shop_sale_no_vat_amount
            sale_amount = export_amount + internal_amount
            return_vat_amount = purchase_taxes_amount - sale_taxes_amount

            value = {
                'month_th': date['month_th'],
                'export_amount': '{0:,.2f}'.format(export_amount),
                'internal_amount': '{0:,.2f}'.format(internal_amount),
                'shop_sale_vat_amount': '{0:,.2f}'.format(shop_sale_vat_amount),
                'shop_sale_no_vat_amount': '{0:,.2f}'.format(shop_sale_no_vat_amount),
                'income_amount': '{0:,.2f}'.format(income_amount),
                'sale_taxes_amount': '{0:,.2f}'.format(sale_taxes_amount),
                'sale_amount': '{0:,.2f}'.format(sale_amount),
                'purchase_amount': '{0:,.2f}'.format(purchase_amount),
                'purchase_taxes_amount': '{0:,.2f}'.format(purchase_taxes_amount),
                'return_vat_amount': '{0:,.2f}'.format(return_vat_amount),
            }
            record.append(value)

        return record


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

        date_results, results, results_shop_sale_vat, results_shop_sale_no_vat, results_sale_taxes, results_purchase = lines._get_results()
        if not results:
            raise UserError(_("Document is empty"))

        date_from_time = self.convert_usertz_to_utc(
            datetime.combine(fields.Date.from_string(lines.date_from), time.min))
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
        worksheet.write(i_row, i_col, str(lines.year), for_left)

        i_row += 2
        i_col = 0
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'เดือน', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ยอดส่งออก', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'ขายในประเทศ', for_center_bold_border)
        i_col += 1
        worksheet.merge_range(i_row, i_col, i_row, i_col + 1, 'ร้านค้าสวัสดิการ', for_center_bold_border)
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

        data_results = lines._get_result_report()

        print('data_resultsssssssssssssssssssss', data_results)

        for data in data_results:
            print('dataaaaaaaaaaaaaaaaaaaaaaaaa', data)
            i_row += 1
            i_col = 0

            internal_amount_cleaned = data['internal_amount'].replace(',', '').replace("'", "")
            shop_sale_vat_amount_cleaned = data['shop_sale_vat_amount'].replace(',', '').replace("'", "")
            sale_taxes_amount = ((float(internal_amount_cleaned) + float(shop_sale_vat_amount_cleaned)) * 7) / 100
            sale_taxes_amount = '{:.2f}'.format(sale_taxes_amount)


            income_amount_cleaned = data['income_amount'].replace(',', '').replace("'", "")
            shop_sale_no_vat_amount_cleaned = data['shop_sale_no_vat_amount'].replace(',', '').replace("'", "")
            income_amount = float(income_amount_cleaned) - float(shop_sale_no_vat_amount_cleaned)

            purchase_taxes_amount_cleaned = data['purchase_taxes_amount'].replace(',', '').replace("'", "")
            return_vat_amount = float(purchase_taxes_amount_cleaned) - float(sale_taxes_amount)



            worksheet.write(i_row, i_col, data['month_th'], for_left_border)
            i_col += 1
            worksheet.write(i_row, i_col, data['export_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['internal_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['shop_sale_vat_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['shop_sale_no_vat_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, income_amount, for_right_border_num_format)
            i_col += 1
            # worksheet.write(i_row, i_col, data['sale_taxes_amount'], for_right_border_num_format)
            worksheet.write(i_row, i_col, sale_taxes_amount, for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['sale_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['purchase_amount'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, data['purchase_taxes_amount'], for_right_border_num_format)
            i_col += 1
            # worksheet.write(i_row, i_col, data['return_vat_amount'], for_right_border_num_format)
            worksheet.write(i_row, i_col, return_vat_amount, for_right_border_num_format)

        workbook.close()
