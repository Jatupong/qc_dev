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

        return self.env['account.move'].search(domain, order='invoice_date')

    def _get_in_invoice(self):
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', ['posted']),
            ('move_type', 'in', ['in_invoice']),
        ]

        return self.env['account.move'].search(domain, order='invoice_date')

    def _get_purchase(self):
        print("_get_purchase")
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['purchase', 'done']),
        ]
        print("Data {}".format(self.env['purchase.order'].search(domain, order='date_order')))

        return self.env['purchase.order'].search(domain, order='date_order')

    def _get_sale(self):
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done']),
        ]

        return self.env['sale.order'].search(domain, order='date_order')

    def convert_usertz_to_utc(self, date_time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        # print('user_tz : ',user_tz)
        tz = pytz.timezone('UTC')
        date_time = user_tz.localize(date_time).astimezone(tz)
        date_time = date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return date_time

    def _get_result_ap_aging(self):
        print("_get_result_ap_aging")
        record = []
        purchase_ids = self._get_purchase()
        if not purchase_ids:
            raise UserError(_("Document is empty."))

        partner_ids = purchase_ids.mapped('partner_id')
        for partner in partner_ids:
            balance_amount_other_currency = 0.0
            balance_amount = 0.0

            credit_limit_amount = partner.credit_limit
            credit_limit = credit_limit_amount


            purchase_by_partner = purchase_ids.filtered(lambda x: x.partner_id == partner).sorted(key=lambda a: a.date_order)
            unpaid_amount = 0.0
            for order in purchase_by_partner:
                print("ID:{}".format(order.id))
                po_no = order.name or ''
                po_amount_total = order.amount_total

                invoice_by_purchase = order.invoice_ids.filtered(lambda x: x.state in ['posted'] and
                                                                           x.payment_state not in ['in_payment', 'paid'])
                invoice_line_ids = invoice_by_purchase.mapped('invoice_line_ids')
                bill_no = ''
                if not invoice_line_ids:
                    amount_currency = 0.0
                    if order.currency_id != order.company_id.currency_id:
                        amount_currency += order.currency_id._convert(po_amount_total,
                                                                      order.company_id.currency_id,
                                                                      order.company_id,
                                                                      order.date_order)
                    else:
                        amount_currency += po_amount_total
                    unpaid_amount += amount_currency
                else:
                    bill_no = invoice_line_ids[0].move_id.name

                move_lines_is_not_deposit = invoice_line_ids.filtered(lambda x: not x.purchase_line_id.is_deposit)
                if move_lines_is_not_deposit:
                    if order.currency_id != order.company_id.currency_id:
                        currency_name = order.currency_id.name
                        amount_other_currency = 0.0
                        currency_rate = order.currency_id._get_rates(order.company_id,
                                                                     move_lines_is_not_deposit[0].date).get(order.currency_id.id)
                        amount_currency = 0.0
                        for line in move_lines_is_not_deposit:
                            price_total = line.price_total
                            amount_other_currency += price_total
                            amount_currency += order.currency_id._convert(price_total,
                                                                          order.company_id.currency_id,
                                                                          order.company_id,
                                                                          line.date)
                            if line.move_id.payment_state == 'paid':
                                unpaid_amount += amount_currency
                    else:
                        amount_other_currency = 0.0
                        currency_rate = ''
                        currency_name = ''
                        amount_currency = sum(move_lines_is_not_deposit.mapped('price_total'))
                else:
                    amount_other_currency = 0.0
                    currency_rate = ''
                    currency_name = ''
                    amount_currency = 0.0

                move_lines_is_deposit = invoice_line_ids.filtered(lambda x: x.purchase_line_id.is_deposit)
                if move_lines_is_deposit:
                    down_payment_date = move_lines_is_deposit[0].invoice_date
                    if order.currency_id != order.company_id.currency_id:
                        currency_name = order.currency_id.name
                        down_payment_amount_other_currency = 0.0
                        currency_rate = order.currency_id._get_rates(order.company_id,
                                                                     move_lines_is_deposit[0].date).get(order.currency_id.id)
                        down_payment_amount = 0.0
                        for line in move_lines_is_deposit:
                            price_total = abs(line.price_total)
                            down_payment_amount_other_currency += price_total
                            down_payment_amount += order.currency_id._convert(price_total,
                                                                              order.company_id.currency_id,
                                                                              order.company_id,
                                                                              line.date)
                            if line.move_id.payment_state == 'paid':
                                unpaid_amount += down_payment_amount
                    else:
                        down_payment_amount_other_currency = 0.0
                        down_payment_amount = abs(sum(move_lines_is_deposit.mapped('price_total')))
                else:
                    down_payment_amount_other_currency = 0.0
                    down_payment_date = ''
                    down_payment_amount = 0.0

                credit_note_ids = self.env['account.move'].search([('reversed_entry_id.id', 'in', invoice_by_purchase.ids),
                                                                   ('state', 'in', ['posted'])])
                if credit_note_ids:
                    credit_note_id = credit_note_ids[0]
                    cn_date = credit_note_id.invoice_date
                    cn_no = credit_note_id.name
                    if credit_note_id.currency_id != credit_note_id.company_currency_id:
                        cn_amount_other_currency = 0.0
                        cn_amount = 0.0
                        for cd in credit_note_ids:
                            cn_amount_other_currency += cd.amount_total
                            cn_amount += cd.currency_id._convert(cd.amount_total,
                                                                 cd.company_currency_id,
                                                                 cd.company_id,
                                                                 cd.invoice_date)
                            if cd.payment_state != 'paid':
                                unpaid_amount += down_payment_amount
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

                balance_amount_other_currency += inv_amount_other_currency
                balance_amount += inv_amount

                invoice_date = invoice_line_ids and min(invoice_line_ids.mapped('move_id').mapped('invoice_date')) or ''
                creditor_age = invoice_date and invoice_date - fields.Date.today() or ''
                invoice_date_due = invoice_line_ids and min(invoice_line_ids.mapped('move_id').mapped('invoice_date_due')) or ''
                credit_limit_note = credit_limit_amount and credit_limit_amount - unpaid_amount
                payment_term = order.payment_term_id.name or ''
                length_payment_term = order.payment_term_id.line_ids and order.payment_term_id.line_ids[0].days or ''

                value = {
                    'ID':order.id,
                    'invoice_date': order.date_order.strftime('%d/%m/%Y') or '',
                    'partner_name': partner.name or '',
                    'pi_no': po_no,
                    'po_amount_total': '{0:,.2f}'.format(po_amount_total),
                    'bill_no': bill_no or '',
                    'payment_term': payment_term or '',
                    'length_payment_term': length_payment_term,
                    'credit_limit': credit_limit and '{0:,.2f}'.format(credit_limit) or '',
                    'due_date': invoice_date_due and invoice_date_due.strftime('%d/%m/%Y') or '',
                    'creditor_age': creditor_age,
                    'currency_name': currency_name,
                    'currency_rate': currency_rate and '{0:,.2f}'.format(currency_rate) or '',
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
                    'credit_limit_note': '{0:,.2f}'.format(credit_limit_note),
                }
                record.append(value)
                print("val {}".format(value))

                credit_limit = 0.0

            value = {
                'invoice_date': '',
                'partner_name': '',
                'pi_no': '',
                'po_amount_total': '',
                'bill_no': '',
                'payment_term': '',
                'length_payment_term': '',
                'credit_limit': '',
                'due_date': '',
                'creditor_age': '',
                'currency_name': '',
                'currency_rate': '',
                'amount_other_currency': '',
                'amount': '',
                'dp_date': '',
                'dp_amount_other_currency': '',
                'dp_amount': '',
                'cn_date': '',
                'cn_no': '',
                'cn_amount_other_currency': '',
                'cn_amount': '',
                'inv_amount_other_currency': '',
                'inv_amount': '',
                'balance_amount_other_currency': '',
                'balance_amount': '',
                'credit_limit_note': '',
            }
            record.append(value)

        return record

    def _get_result_ar_aging(self):
        print("_get_result_ar_aging")
        record = []
        sale_ids = self._get_sale()
        if not sale_ids:
            raise UserError(_("Document is empty."))

        partner_ids = sale_ids.mapped('partner_id')
        for partner in partner_ids:
            balance_amount_other_currency = 0.0
            balance_amount = 0.0

            credit_limit_amount = partner.credit_limit
            credit_limit = credit_limit_amount

            sale_by_partner = sale_ids.filtered(lambda x: x.partner_id == partner)
            unpaid_amount = 0.0

            for order in sale_by_partner:
                so_no = order.name or ''
                so_amount_total = order.amount_total

                invoice_by_sale = order.invoice_ids.filtered(lambda x: x.state in ['posted'] and
                                                                       x.payment_state not in ['in_payment', 'paid'])
                invoice_line_ids = invoice_by_sale.mapped('invoice_line_ids')
                move_name = ''
                if not invoice_line_ids:
                    amount_currency = 0.0
                    if order.currency_id != order.company_id.currency_id:
                        amount_currency += order.currency_id._convert(so_amount_total,
                                                                      order.company_id.currency_id,
                                                                      order.company_id,
                                                                      order.date_order)
                    else:
                        amount_currency += so_amount_total
                    unpaid_amount += amount_currency
                else:
                    move_name = invoice_line_ids[0].move_id.name

                move_lines_is_not_downpayment = invoice_line_ids.filtered(lambda x: not x.is_downpayment)
                if move_lines_is_not_downpayment:
                    if order.currency_id != order.company_id.currency_id:
                        currency_name = order.currency_id.name
                        amount_other_currency = 0.0
                        currency_rate = order.currency_id._get_rates(order.company_id,
                                                                     move_lines_is_not_downpayment[0].date).get(
                            order.currency_id.id)
                        amount_currency = 0.0
                        for line in move_lines_is_not_downpayment:
                            price_total = line.price_total
                            amount_other_currency += price_total
                            amount_currency += order.currency_id._convert(price_total,
                                                                          order.company_id.currency_id,
                                                                          order.company_id,
                                                                          line.date)
                            if line.move_id.payment_state == 'paid':
                                unpaid_amount += amount_currency
                    else:
                        amount_other_currency = 0.0
                        currency_rate = ''
                        currency_name = ''
                        amount_currency = sum(move_lines_is_not_downpayment.mapped('price_total'))
                else:
                    amount_other_currency = 0.0
                    currency_rate = ''
                    currency_name = ''
                    amount_currency = 0.0

                move_lines_is_downpayment = invoice_line_ids.filtered(lambda x: x.purchase_line_id.is_deposit)
                if move_lines_is_downpayment:
                    down_payment_date = move_lines_is_downpayment[0].invoice_date
                    if order.currency_id != order.company_id.currency_id:
                        currency_name = order.currency_id.name
                        down_payment_amount_other_currency = 0.0
                        currency_rate = order.currency_id._get_rates(order.company_id,
                                                                     move_lines_is_downpayment[0].date).get(
                            order.currency_id.id)
                        down_payment_amount = 0.0
                        for line in move_lines_is_downpayment:
                            price_total = line.price_total
                            down_payment_amount_other_currency += price_total
                            down_payment_amount += order.currency_id._convert(price_total,
                                                                              order.company_id.currency_id,
                                                                              order.company_id,
                                                                              line.date)
                            if line.move_id.payment_state == 'paid':
                                unpaid_amount += down_payment_amount
                    else:
                        down_payment_amount_other_currency = 0.0
                        down_payment_amount = abs(sum(move_lines_is_downpayment.mapped('price_total')))
                else:
                    down_payment_amount_other_currency = 0.0
                    down_payment_date = ''
                    down_payment_amount = 0.0

                credit_note_ids = self.env['account.move'].search([('reversed_entry_id.id', 'in', invoice_by_sale.ids),
                                                                   ('state', 'in', ['posted'])])
                if credit_note_ids:
                    credit_note_id = credit_note_ids[0]
                    cn_date = credit_note_id.invoice_date
                    cn_no = credit_note_id.name
                    if credit_note_id.currency_id != credit_note_id.company_currency_id:
                        cn_amount_other_currency = 0.0
                        cn_amount = 0.0
                        for cd in credit_note_ids:
                            cn_amount_other_currency += cd.amount_total
                            cn_amount += cd.currency_id._convert(cd.amount_total,
                                                                 cd.company_currency_id,
                                                                 cd.company_id,
                                                                 cd.invoice_date)
                            if cd.payment_state != 'paid':
                                unpaid_amount += down_payment_amount
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

                balance_amount_other_currency += inv_amount_other_currency
                balance_amount += inv_amount

                invoice_date = invoice_line_ids and min(invoice_line_ids.mapped('move_id').mapped('invoice_date')) or ''
                creditor_age = invoice_date and invoice_date - fields.Date.today() or ''
                invoice_date_due = invoice_line_ids and min(
                    invoice_line_ids.mapped('move_id').mapped('invoice_date_due')) or ''
                credit_limit_note = credit_limit_amount and credit_limit_amount - unpaid_amount
                payment_term = order.payment_term_id.name or ''
                length_payment_term = order.payment_term_id.line_ids and order.payment_term_id.line_ids[0].days or ''

                value = {
                    'team_name': order.team_id.name or '',
                    'invoice_date': order.date_order.strftime('%d/%m/%Y') or '',
                    'partner_name': partner.name or '',
                    'so_no': so_no,
                    'so_amount_total': so_amount_total,
                    'move_name': move_name or '',
                    'payment_term': payment_term,
                    'length_payment_term': length_payment_term,
                    'credit_limit_amount': '{0:,.2f}'.format(credit_limit) or '',
                    'due_date': invoice_date_due and invoice_date_due.strftime('%d/%m/%Y') or '',
                    'creditor_age': creditor_age or '',
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
                    'credit_limit_note': '{0:,.2f}'.format(credit_limit_note),
                }
                record.append(value)

                credit_limit = 0.0

            value = {
                'team_name': '',
                'invoice_date': '',
                'partner_name': '',
                'so_no': '',
                'so_amount_total': '',
                'move_name': '',
                'payment_term': '',
                'length_payment_term': '',
                'credit_limit_amount': '',
                'due_date': '',
                'creditor_age': '',
                'currency_name': '',
                'currency_rate': '',
                'amount_other_currency': '',
                'amount': '',
                'dp_date': '',
                'dp_amount_other_currency': '',
                'dp_amount': '',
                'cn_date': '',
                'cn_no': '',
                'cn_amount_other_currency': '',
                'cn_amount': '',
                'inv_amount_other_currency': '',
                'inv_amount': '',
                'balance_amount_other_currency': '',
                'balance_amount': '',
                'credit_limit_note': '',
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
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อัตราแลกเปลี่ยน', for_center_bold_border)
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
            if self.user_has_groups('base.group_no_one'):
                i_col = 0
                i_row += 1
                worksheet.merge_range(i_row, i_col,i_row, i_col + 20, str(move), for_center_date)
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
            worksheet.write(i_row, i_col, move['length_payment_term'], for_right_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['credit_limit'], for_right_border_num_format)
            i_col += 1
            worksheet.write(i_row, i_col, move['due_date'], for_center_date)
            i_col += 1
            worksheet.write(i_row, i_col, move['creditor_age'], for_right_border)
            i_col += 1
            worksheet.write(i_row, i_col, move['currency_name'], for_right_border_num_format)
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
            worksheet.write(i_row, i_col, move['credit_limit_note'], for_right_border_num_format)

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
        worksheet.merge_range(i_row, i_col, i_row + 1, i_col, 'อัตราแลกเปลี่ยน', for_center_bold_border)
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
            worksheet.write(i_row, i_col, move['credit_limit_note'], for_right_border_num_format)

        workbook.close()
