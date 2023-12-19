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


class WizardSaleReport(models.TransientModel):
    _name = 'wizard.sale.report'
    _description = 'Wizard Sale Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    team_id = fields.Many2one('crm.team', string='Team')
    product_ids = fields.Many2many('product.product', 'product_sale_report_ref', string='Products', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_category_ids = fields.Many2many('product.category', 'product_category_sale_report_ref', string='Categories')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.model
    def default_get(self, fields):
        res = super(WizardSaleReport, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})

        return res

    def print_report_excel(self):
        [data] = self.read()
        data = {'form': data}

        return self.env.ref('qc_sale_report.sale_report_xls').report_action([], data=data, config=False)

    def _get_invoice_line(self):
        domain = [
            ('move_id.invoice_date', '>=', self.date_from),
            ('move_id.invoice_date', '<=', self.date_to),
            ('move_id.move_type', 'in', ['out_invoice']),
            ('move_id.state', 'in', ['posted']),
            ('sale_line_ids', '!=', False),
        ]

        return self.env['account.move.line'].search(domain, order='invoice_date')

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time

    def _get_result_sale(self):
        record = []
        invoice_line_ids = self._get_invoice_line()
        if not invoice_line_ids:
            raise UserError(_("Document is empty."))

        invoice_ids = invoice_line_ids.mapped('move_id')
        for move in invoice_ids:
            invoice_line_ids_by_move = invoice_line_ids.filtered(lambda x: x.move_id == move)
            qty_shipped_total = 0.0
            amount_total = 0.0
            sale_price_total = 0.0
            rebate_other_currency_total = 0.0
            rebate_total = 0.0
            comm_other_currency_total = 0.0
            comm_total = 0.0
            net_other_currency_total = 0.0
            net_total = 0.0

            for line in invoice_line_ids_by_move:
                sale_line_id = line.sale_line_ids[0]
                sale_id = sale_line_id.order_id

                qty_shipped_total += 0.0
                amount_total += line.price_subtotal
                sale_price_total += 0.0
                rebate_other_currency_total += 0.0
                rebate_total += 0.0
                comm_other_currency_total += 0.0
                comm_total += 0.0
                net_other_currency_total += 0.0
                net_total += 0.0

                value = {
                    'team': sale_id.team_id.name,
                    'channel': sale_id.source_id.name or '',
                    'customer': sale_id.partner_id.name,
                    'area': sale_id.partner_id.area_type or '',
                    'region': sale_id.partner_id.region or '',
                    'country': line.move_id.partner_id.country_id.name or '',
                    'invoice_no': line.move_id.name,
                    'loading_date': '',
                    'pi_no': sale_id.name,
                    'currency': sale_id.currency or '',
                    # 'currency_rate': line.move_id.customer_department,
                    'currency_rate': '',
                    'currency_avg': '',
                    'item_code': line.product_id.default_code or '',
                    'description': line.name,
                    'qty_shipped': '',
                    'net_price': '',
                    'unit_price': line.price_unit,
                    'amount': line.price_subtotal,
                    'sale_price': '',
                    'handtag': '',
                    'special_sticker': '',
                    'color_box_unit': '',
                    'color_box_other_currency': '',
                    'cost': '',
                    'discount_other_currency': '',
                    'discount': '',
                    'rebate_other_currency': '',
                    'rebate': '',
                    'comm_other_currency': '',
                    'comm': '',
                    'net_other_currency': '',
                    'net': '',
                    'standard_cost': '',
                    'margin': '',
                    'margin_percent': sale_line_id.margin,
                }
                record.append(value)

            value = {
                'team': 'total',
                'channel': '',
                'customer': '',
                'area': '',
                'region': '',
                'country': '',
                'invoice_no': '',
                'loading_date': '',
                'pi_no': '',
                'currency': '',
                'currency_rate': '',
                'currency_avg': '',
                'item_code': '',
                'description': '',
                'qty_shipped': qty_shipped_total,
                'net_price': '',
                'unit_price': '',
                'amount': amount_total,
                'sale_price': sale_price_total,
                'handtag': '',
                'special_sticker': '',
                'color_box_unit': '',
                'color_box_other_currency': '',
                'cost': '',
                'discount_other_currency': '',
                'discount': '',
                'rebate_other_currency': rebate_other_currency_total,
                'rebate': rebate_total,
                'comm_other_currency': comm_other_currency_total,
                'comm': comm_total,
                'net_other_currency': net_other_currency_total,
                'net': net_total,
                'standard_cost': '',
                'margin': '',
                'margin_percent': '',
            }
            record.append(value)

        return record


class WizardSaleReportXls(models.AbstractModel):
    _name = 'report.qc_sale_report.sale_report_xls'
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

        record_list = lines._get_result_sale()

        worksheet = workbook.add_worksheet('Page 1')
        i_row = 1
        worksheet.merge_range(i_row, 0, i_row, 20, lines.company_id.name, for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'Sale Report', for_center_bold)
        i_row += 1
        worksheet.merge_range(i_row, 0, i_row, 20, 'ณ ' + str(fields.Date.today().strftime("%d/%m/%Y")), for_center_bold)

        i_row += 1
        i_col = 0
        worksheet.write(i_row, i_col, 'Team', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ช่องทางการจำหน่าย', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Customer', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'AREA', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'REGION', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'COUNTRY', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Invoice No.', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Loading \n Date', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'PI NO.', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'สกุลเงิน', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'อัตราแลก \n เปลี่ยน', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'อัตราขายถัว \n เฉลี่ย', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Item Code', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Description', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, '**QTY \n Shipped', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Net Price', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Unit Price', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Amount', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ราคาขาย \n (เฉพาะค่าแวร์)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ค่า Handtag', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Special sticker', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ค่ากล่องสีต่อ \n หน่วย', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ค่ากล่องสี \n (USD)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Charge \n มีต้นทุน(THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ส่วนลดการค้า \n (USD)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ส่วนลดการค้า \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ส่วนลด Rebate \n (USD)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'ส่วนลด Rebate \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, '- Comm.', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, '- Comm. \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Net', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Net \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'standard cost \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Margin \n (THB)', for_center_bold_border)
        i_col += 1
        worksheet.write(i_row, i_col, 'Margin \n (%)', for_center_bold_border)

        for rec in record_list:
            if rec['team'] != 'total':
                i_col = 0
                i_row += 1
                worksheet.write(i_row, i_col, rec['team'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['channel'], for_center_date)
                i_col += 1
                worksheet.write(i_row, i_col, rec['customer'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['area'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['region'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['country'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['invoice_no'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['loading_date'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['pi_no'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency_rate'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency_avg'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['item_code'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['description'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['qty_shipped'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net_price'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['unit_price'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['amount'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['sale_price'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['handtag'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['special_sticker'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['color_box_unit'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['color_box_other_currency'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['cost'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['discount_other_currency'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['discount'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['rebate_other_currency'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['rebate'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['comm_other_currency'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['comm'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net_other_currency'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['standard_cost'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['margin'], for_right_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['margin_percent'], for_right_border_num_format)
            else:
                i_col = 0
                i_row += 1
                worksheet.write(i_row, i_col, '', for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['channel'], for_center_date)
                i_col += 1
                worksheet.write(i_row, i_col, rec['customer'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['area'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['region'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['country'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['invoice_no'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['loading_date'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['pi_no'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency_rate'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['currency_avg'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['item_code'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['description'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['qty_shipped'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net_price'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['unit_price'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['amount'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['sale_price'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['handtag'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['special_sticker'], for_left_border)
                i_col += 1
                worksheet.write(i_row, i_col, rec['color_box_unit'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['color_box_other_currency'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['cost'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['discount_other_currency'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['discount'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['rebate_other_currency'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['rebate'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['comm_other_currency'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['comm'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net_other_currency'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['net'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['standard_cost'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['margin'], for_right_bold_border_num_format)
                i_col += 1
                worksheet.write(i_row, i_col, rec['margin_percent'], for_right_bold_border_num_format)

        workbook.close()
