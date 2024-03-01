# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import models, fields, api, _
from datetime import datetime
#from StringIO import StringIO
from io import BytesIO
import base64
from odoo.exceptions import UserError
from odoo.tools import misc
import xlwt
from decimal import *
from dateutil.relativedelta import relativedelta
import calendar
from io import StringIO
import xlsxwriter



#this is for tax report section
class tax_report(models.TransientModel):
    _name = 'tax.report'



    def _get_year(self):
        curr_date = datetime.now()
        last_year = curr_date.year - 1 + 543
        current_year = curr_date.year + 543
        next_year = curr_date.year + 1 + 543

        return [(last_year, last_year), (current_year, current_year), (next_year, next_year)]

    cuctomer = fields.Many2one(string='Customer',comodel_name='res.partner')
    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)
    month = fields.Selection([
        ('1','มกราคม'),
        ('2','กุมภาพันธ์'),
        ('3', 'มีนาคม'),
        ('4', 'เมษายน'),
        ('5', 'พฤษภาคม'),
        ('6', 'มิถุนายน'),
        ('7', 'กรกฏาคม'),
        ('8', 'สิงหาคม'),
        ('9', 'กันยายน'),
        ('10', 'ตุลาคม'),
        ('11', 'พฤศจิกายน'),
        ('12', 'ธันวาคม'),
    ],string='Month',required=True)
    year = fields.Integer(string='Year')
    report_type = fields.Selection([('sale','ภาษีขาย'),('purchase','ภาษีซื้อ')],default='sale',string='Report Type', required=True)
    #partner_id = fields.Many2one('res.partner', string='Partner')
    tax_id = fields.Many2one('account.tax', string='Tax Type',required=False)
    # disable_excel_tax_report = fields.Boolean(string="Disable Tax Report in Excel Format")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    company_id = fields.Many2one('res.company')
    include_no_vat = fields.Boolean(string='Include No Vat')
    vat_0 = fields.Boolean('Vat 0')




    @api.model
    def default_get(self, fields):
        res = super(tax_report,self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year,curr_date.month,1).date() or False
        to_date = datetime(curr_date.year,curr_date.month,calendar.monthrange(curr_date.year, curr_date.month)[1]).date() or False
        year = curr_date.year + 543
        # disable_excel_tax_report = self.env.user.company_id.disable_excel_tax_report
        company_id = self.env.company.id
        res.update({'year': year,'month':str(curr_date.month),
                    'date_from': str(from_date),
                    'date_to': str(to_date),'company_id': company_id,})
        print ('default get')
        print (res)
        return res

    @api.onchange('month','year')
    def onchange_month_year(self):
        if self.month and self.year:
            select_month = self.month
            select_year = self.year - 543
            month_day = calendar.monthrange(select_year, int(select_month))[1]
            from_date = datetime(select_year, int(select_month), 1).date() or False
            to_date = datetime(select_year, int(select_month), month_day).date() or False
            self.date_from = from_date
            self.date_to = to_date

    @api.onchange('report_type')
    def onchange_report_type(self):
        result = {}
        if self.report_type == 'sale':
            self.tax_id = self.env['account.tax'].search([('type_tax_use','=','sale'),('company_id','=',self.company_id.id),('tax_report','=',True)],limit=1)
            result['domain'] = {'tax_id': [('type_tax_use','=','sale'),('wht','=',False)]}
        if self.report_type == 'purchase':
            self.tax_id = self.env['account.tax'].search(
                [('type_tax_use', '=', 'purchase'), ('company_id', '=', self.company_id.id), ('tax_report', '=', True)],
                limit=1)
            result['domain'] = {'tax_id': [('type_tax_use','=','purchase'),('wht','=',False)]}

        return result

    # def generate_report(self):
    #     data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.pos_config_ids.ids}
    #     return self.env.ref('point_of_sale.sale_details_report').report_action([], data=data)

    def print_report_pdf(self):
        print('xxxxxxxxxxxxxxxxxxxxx')
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type, 'tax_id': self.tax_id.id, 'company_id': self.company_id,'vat_0':self.vat_0,'customer':self.cuctomer.name}
        # data['form'] = self.read(['date_from', 'date_to', 'report_type', 'tax_id', 'operating_unit_id','company_id','include_no_vat'])[0]
        # print ('------DATA---')
        # print (data)
        if data['report_type'] == 'sale':
            # return self.env['report'].get_action(self, 'thai_accounting.sale_tax_report_id', data=data)
            return self.env.ref('PJD_report.action_sale_tax_report_id').report_action([], data=data)
        else:
            # return self.env['report'].get_action(self, 'thai_accounting.purchase_tax_report_id', data=data)
            return self.env.ref('PJD_report.action_purchase_tax_report_id').report_action([], data=data)
    def print_report_pdf2(self):
        print('xxxxxxxxxxxxxxxxxxxxx')
        self.report_type = 'sale'
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type, 'tax_id': self.tax_id.id, 'company_id': self.company_id,'vat_0':self.vat_0,'customer':self.cuctomer.name}
        if data['report_type'] == 'sale':
            return self.env.ref('PJD_report.action_sale_tax_report_id2').report_action([], data=data)
        else:
            return self.env.ref('PJD_report.action_purchase_tax_report_id').report_action([], data=data)


    def get_amount_multi_currency(self,move_id):
        total_amount = 0.0
        tax_amount = 0.0
        for line in move_id.line_ids:
            total_amount += abs(line.debit)
            if line.account_id.sale_tax_report:
                tax_amount += abs(line.balance)

        return total_amount,tax_amount

    def convert_list_to_string(org_list, seperator=' '):
        """ Convert list to string, by joining all item in list with given separator.
            Returns the concatenated string """
        return seperator.join(org_list)

    def print_report(self):
        print('print_report_xls')
        fl = BytesIO()
        workbook = xlsxwriter.Workbook(fl)
        name = self.report_type + '_tax_report'
        namexls = str(self.report_type) + '_tax_report' + '.xls'
        worksheet = workbook.add_worksheet(name)

        for_left_bold_no_border = workbook.add_format({'align': 'left', 'bold': True})
        for_center_bold_no_border = workbook.add_format({'align': 'center', 'bold': True})
        for_right_bold_no_border = workbook.add_format({'align': 'right', 'bold': True})

        for_left_no_border = workbook.add_format({'align': 'left'})
        for_center_no_border = workbook.add_format({'align': 'center'})
        for_right_no_border = workbook.add_format({'align': 'right'})

        for_left_bold = workbook.add_format({'align': 'left', 'bold': True, 'border': True})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True, 'border': True})
        for_right_bold = workbook.add_format({'align': 'right', 'bold': True, 'border': True})

        for_left = workbook.add_format({'align': 'left', 'border': True})
        for_center = workbook.add_format({'align': 'center', 'border': True})
        for_right = workbook.add_format({'align': 'right', 'border': True , 'num_format': '#,##0.00'})

        for_right_bold_no_border_date = workbook.add_format({'align': 'right', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format({'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0.00'})

        for_center_bold_no_border_date = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_left_bold_no_border_date = workbook.add_format({'align': 'left', 'bold': True, 'num_format': 'dd/mm/yy'})

        for_center_date = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy'})

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 10)

        month = self.month
        print (month)
        print('==============')

        if month:
            if month == '1':
                monthth = 'มกราคม'
            elif month == '2':
                monthth = 'กุมภาพันธ์'
            elif month == '3':
                monthth = 'มีนาคม'
            elif month == '3':
                monthth = 'มีนาคม'
            elif month == '4':
                monthth = 'เมษายน'
            elif month == '5':
                monthth = 'พฤษภาคม'
            elif month == '6':
                monthth = 'มิถุนายน'
            elif month == '7':
                monthth = 'กรกฏาคม'
            elif month == '8':
                monthth = 'สิงหาคม'
            elif month == '9':
                monthth = 'กันยายน'
            elif month == '10':
                monthth = 'ตุลาคม'
            elif month == '11':
                monthth = 'พฤศจิกายน'
            else:
                monthth = 'ธันวาคม'

        year = self.year
        company_id = self.env.company

        inv_row = 3
        worksheet.write(inv_row, 0, 'เดือนภาษี', for_left_bold_no_border)
        worksheet.write(inv_row, 1, monthth, for_left_no_border)
        worksheet.write(inv_row, 4, 'ปี', for_left_bold_no_border)
        worksheet.write(inv_row, 5, year, for_left_no_border)

        inv_row += 1
        worksheet.write(inv_row, 0, 'ชื่อผู้ประกอบการ', for_left_bold_no_border)
        worksheet.write(inv_row, 1, company_id.name, for_left_no_border)
        worksheet.write(inv_row, 4, 'เลขประจำผู้เสียภาษีอากร', for_left_bold_no_border)
        worksheet.write(inv_row, 5, company_id.vat, for_left_no_border)

        inv_row += 1
        worksheet.write(inv_row, 0, 'ชื่อสถานประกอบการ', for_left_bold_no_border)
        worksheet.write(inv_row, 1, company_id.name, for_left_no_border)
        worksheet.write(inv_row, 4, 'สำนักงานใหญ่ / สาขา', for_left_bold_no_border)
        if company_id.branch_no:
            if company_id.branch_no == '00000':
                branch_no = 'สำนักงานใหญ่'
            else:
                branch_no = 'สาขา' + ' ' + company_id.branch_no
            # branch_no = company_id.branch_no if company_id.branch_no == '00000' else 'สำนักงานใหญ่'
            worksheet.write(inv_row, 5, branch_no, for_left_no_border)
        else:
            worksheet.write(inv_row, 5, 'สำนักงานใหญ่', for_left_no_border)


        inv_row += 1
        worksheet.write(inv_row, 0, 'สถานประกอบการ', for_left_bold_no_border)
        company_address = company_id.get_company_full_address_text()
        worksheet.write(inv_row, 1,company_address , for_left_no_border)


        inv_row += 3
        inv_row_merge_head = inv_row + 1
        worksheet.merge_range('A' + str(inv_row) + ':A' + str(inv_row_merge_head), "ลำดับที่", for_center_bold)
        worksheet.merge_range('B' + str(inv_row) + ':C' + str(inv_row), "ใบกำกับภาษี", for_center_bold)
        worksheet.write('B' + str(inv_row_merge_head), 'วัน เดือน ปี', for_center_bold)
        worksheet.write('C' + str(inv_row_merge_head), 'เลขที่', for_center_bold)
        worksheet.merge_range('D' + str(inv_row) + ':D' + str(inv_row_merge_head), "ชื่อผู้ซื้อสินค้า/ผู้รับบริการ",
                              for_center_bold)
        worksheet.merge_range('E' + str(inv_row) + ':E' + str(inv_row_merge_head),
                              'เลขประจำตัวผู้เสียภาษีอากร\nของผู้ซื้อสินค้า/ผู้รับบริการ', for_center_bold)
        worksheet.merge_range('F' + str(inv_row) + ':G' + str(inv_row), "สถานประกอบการ", for_center_bold)
        worksheet.write('F' + str(inv_row_merge_head), 'สำนักงานใหญ่', for_center_bold)
        worksheet.write('G' + str(inv_row_merge_head), 'สาขาที่', for_center_bold)
        worksheet.merge_range('H' + str(inv_row) + ':H' + str(inv_row_merge_head), "มูลค่าสินค้าหรือบริการ",
                              for_center_bold)
        worksheet.merge_range('I' + str(inv_row) + ':I' + str(inv_row_merge_head), "จำนวนเงินภาษีมูลค่าเพิ่ม",
                              for_center_bold)
        worksheet.merge_range('J' + str(inv_row) + ':J' + str(inv_row_merge_head), "รวม",
                              for_center_bold)
        worksheet.merge_range('K' + str(inv_row) + ':K' + str(inv_row_merge_head), "หมายเหตุ",
                              for_center_bold)

        data = {}
        # data = self.read(['date_from', 'date_to', 'month', 'year', 'report_type', 'tax_id', 'company_id'])[0]
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type, 'tax_id': self.tax_id.id, 'company_id': self.company_id,'vat_0':self.vat_0}

        if self.report_type == 'sale':
            report_values = self.env['report.PJD_report.sale_tax_report_id']._get_report_values(self,
                                                                                                            data=data)
            print('report_values : ', report_values)
            invoice_ids = {}
            invoices = report_values.get('docs')
            # for invoice_id in invoices:
            #     print('invoice_id:',invoice_id)
            #     # invoice_ids={
            #     #     'date': invoices
            #     # }
            print('report_values : ', report_values)

            if self.tax_id.tax_report:
                worksheet.merge_range('A1:I1', "รายงานภาษีขาย", for_center_bold_no_border)
            else:
                worksheet.merge_range('A1:I1', "รายงานภาษีขาย", for_center_bold_no_border)
            amount_untaxed = 0
            amount_vat = 0
            amount_total = 0
            print('invoices:',invoices)
            if invoices:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                for inv in invoices:
                    inv_row += 1
                    worksheet.write(inv_row, 0, sl_no, for_center)
                    worksheet.write(inv_row, 1, inv['date'] or '', for_center_date)
                    worksheet.write(inv_row, 2, inv['name'], for_center)

                    worksheet.write(inv_row, 3, inv['partner'], for_left)
                    worksheet.write(inv_row, 4, inv['vat'], for_left)

                    if inv['branch'] == '00000':
                        worksheet.write(inv_row, 5, inv['branch'], for_right)
                        worksheet.write(inv_row, 6, '', for_left)
                    else:
                        worksheet.write(inv_row, 5, '', for_left)
                        worksheet.write(inv_row, 6, inv['branch'], for_right)

                    if inv['state'] != 'cancel':
                        if inv['type'] == 'out_refund':

                            worksheet.write(inv_row, 7, inv['amount_untaxed'] * (-1), for_right)
                            amount_untaxed = amount_untaxed + (inv['amount_untaxed'] * (-1))
                            amount_vat = amount_vat + (inv['amount_tax'] * (-1))
                            amount_total = amount_total + (inv['amount_total'] * (-1))
                            worksheet.write(inv_row, 8, inv['amount_tax'] * (-1), for_right)
                            worksheet.write(inv_row, 9, inv['amount_total'] * (-1), for_right)
                        else:
                            # if inv['move_id'].discount_value:
                            #     print('dd',inv['untaxed_amount_after_discount'])
                            #     worksheet.write(inv_row, 7, inv['untaxed_amount_after_discount'], for_right)
                            #     amount_untaxed = amount_untaxed + inv['untaxed_amount_after_discount']
                            #
                            # else:
                            #     print('sssssssssssssss')
                            #
                            worksheet.write(inv_row, 7, inv['amount_untaxed'], for_right)
                            amount_untaxed = amount_untaxed + inv['amount_untaxed']
                            amount_vat = amount_vat + inv['amount_tax']
                            amount_total = amount_total + inv['amount_total']
                            worksheet.write(inv_row, 8, inv['amount_tax'], for_right)
                            worksheet.write(inv_row, 9, inv['amount_total'], for_right)

                    if inv['state'] == 'cancel':
                        worksheet.write(inv_row, 7, 0, for_right)
                        worksheet.write(inv_row, 8, 0, for_right)
                        worksheet.write(inv_row, 9, 0, for_right)
                        worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                    else:
                        worksheet.write(inv_row, 10, ' ', for_right)



                    sl_no += 1

                inv_row += 1
                worksheet.write(inv_row, 6, 'Total', for_center_bold)
                worksheet.write(inv_row, 7, amount_untaxed, for_right_bold_border_num_format)
                worksheet.write(inv_row, 8, amount_vat, for_right_bold_border_num_format)
                worksheet.write(inv_row, 9, amount_total, for_right_bold_border_num_format)

        else:
            report_values = self.env['report.PJD_report.purchase_tax_report_id']._get_report_values(self,data=data)
            move_lines = report_values.get('docs')
            print('move_lines : ', move_lines)

            if self.tax_id.tax_report:
                worksheet.merge_range('A1:I1', "รายงานภาษีซื้อ", for_center_bold_no_border)
            else:
                worksheet.merge_range('A1:I1', "รายงานภาษีซื้อ", for_center_bold_no_border)
            amount_total = 0
            before_total = 0
            amount_tax_total = 0
            if move_lines:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                amount_tax = amount_untax = 0.0
                for ml in move_lines:
                    print('ml:',ml)
                    inv_row += 1
                    worksheet.write(inv_row, 0, sl_no, for_center)

                    worksheet.write(inv_row, 1, ml['date'] or '', for_center_date)

                    worksheet.write(inv_row, 2, ml['ref'], for_left)
                    worksheet.write(inv_row, 3, ml['partner'].name, for_left)
                    worksheet.write(inv_row, 4, ml['vat'], for_left)
                    if ml['branch'] == '00000':
                        worksheet.write(inv_row, 5, ml['branch'], for_right)
                        worksheet.write(inv_row, 6, '', for_left)
                    else:
                        worksheet.write(inv_row, 5, ' ', for_left)
                        worksheet.write(inv_row, 6, ml['branch'], for_right)
                    if ml['debit']:
                        amount_tax = ml['debit']
                    elif ml['credit']:
                        amount_tax = ml['credit']
                    else:
                        amount_tax = 0

                    if ml['amount_untaxed']:
                        if ml['type'] == 'in_refund':
                            if ml['amount_untaxed'] > 0:
                                amount_untax = ml['amount_untaxed'] * (-1)
                            else:
                                amount_untax = ml['amount_untaxed']
                        else:
                            amount_untax = ml['amount_untaxed']
                    else:
                        amount_untax = amount_tax * 100 / 7

                    if ml['type'] == 'in_refund':
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                            else:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                                before_total += amount_untax
                        else:
                            if ml['debit']:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                            else:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                    else:
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                            else:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                                before_total += amount_untax
                        else:
                            if ml['debit']:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                            else:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax

                    if ml['type'] == 'in_refund':
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                debit_credit = ml['debit']
                            elif ml['credit']:
                                debit_credit = ml['credit']
                            worksheet.write(inv_row, 8, '0.00', for_right_border_num_format)
                            worksheet.write(inv_row, 9, '0.00', for_right_border_num_format)
                            amount_total += '0.00' + amount_untax
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                        else:
                            if ml['debit']:
                                debit_credit = ml['debit']
                            elif ml['credit']:
                                debit_credit = ml['credit']
                            worksheet.write(inv_row, 8, ml['debit'] or ml['credit'] * (-1), for_right_border_num_format)
                            worksheet.write(inv_row, 9, (debit_credit * (-1) + amount_untax), for_right_border_num_format)
                            amount_total += (debit_credit * (-1)) + amount_untax
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                            worksheet.write(inv_row, 10, ml['note'], for_right)

                    else:
                        if ml['state'] == 'cancel':
                            worksheet.write(inv_row, 8,'0.00', for_right_border_num_format)
                            worksheet.write(inv_row, 9, '0.00',for_right_border_num_format)
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                        else:
                            worksheet.write(inv_row, 8, ml['debit'] or ml['credit'], for_right_border_num_format)
                            worksheet.write(inv_row, 9, ml['debit'] + ml['credit'] + amount_untax,for_right_border_num_format)
                            amount_total += ml['debit'] + ml['credit'] + amount_untax
                            worksheet.write(inv_row, 10, ml['note'], for_right)

                    sl_no += 1
                    if ml['type'] == 'in_refund':
                        if ml['state'] != 'cancel':
                            amount_tax_total += ml['debit'] * (-1)
                            amount_tax_total += ml['credit'] * (-1)
                    else:
                        if ml['state'] != 'cancel':
                            amount_tax_total += ml['debit']
                            amount_tax_total += ml['credit']

                inv_row += 1
                worksheet.write(inv_row, 6, 'Total', for_center_bold)
                worksheet.write(inv_row, 7, before_total, for_right_bold_border_num_format)
                worksheet.write(inv_row, 8, amount_tax_total, for_right_bold_border_num_format)
                worksheet.write(inv_row, 9, amount_total , for_right_bold_border_num_format)


        workbook.close()
        buf = fl.getvalue()
        # vals = {'name': namexls, 'report_file': base64.encodestring(buf)}
        vals = {'name': namexls, 'report_file': base64.encodebytes(buf)}
        self._cr.execute("TRUNCATE tax_excel_export CASCADE")
        wizard_id = self.env['tax.excel.export'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.excel.export',
            'target': 'new',
            'res_id': wizard_id.id,
        }

    def print_report2(self):
        print('print_report_xls2')
        fl = BytesIO()
        workbook = xlsxwriter.Workbook(fl)
        name = self.report_type + '_tax_report2'
        namexls = str(self.report_type) + '_tax_report2' + '.xls'
        worksheet = workbook.add_worksheet(name)

        for_left_bold_no_border = workbook.add_format({'align': 'left', 'bold': True})
        for_center_bold_no_border = workbook.add_format({'align': 'center', 'bold': True})
        for_right_bold_no_border = workbook.add_format({'align': 'right', 'bold': True})

        for_left_no_border = workbook.add_format({'align': 'left'})
        for_center_no_border = workbook.add_format({'align': 'center'})
        for_right_no_border = workbook.add_format({'align': 'right'})

        for_left_bold = workbook.add_format({'align': 'left', 'bold': True, 'border': True})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True, 'border': True})
        for_center_bold_bg = workbook.add_format({'align': 'center', 'bold': True, 'border': True,'bg_color': '#E1F5FE'})
        for_right_bold = workbook.add_format({'align': 'right', 'bold': True, 'border': True})

        for_left = workbook.add_format({'align': 'left', 'border': True})
        for_center = workbook.add_format({'align': 'center', 'border': True})
        for_right = workbook.add_format({'align': 'right', 'border': True , 'num_format': '#,##0.00'})

        for_right_bold_no_border_date = workbook.add_format({'align': 'right', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format({'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0.00'})

        for_center_bold_no_border_date = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_left_bold_no_border_date = workbook.add_format({'align': 'left', 'bold': True, 'num_format': 'dd/mm/yy'})

        for_center_date = workbook.add_format({'align': 'center', 'border': True, 'num_format': 'dd/mm/yyyy'})

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)

        month = self.month
        print (month)
        print('==============')

        if month:
            if month == '1':
                monthth = 'มกราคม'
            elif month == '2':
                monthth = 'กุมภาพันธ์'
            elif month == '3':
                monthth = 'มีนาคม'
            elif month == '3':
                monthth = 'มีนาคม'
            elif month == '4':
                monthth = 'เมษายน'
            elif month == '5':
                monthth = 'พฤษภาคม'
            elif month == '6':
                monthth = 'มิถุนายน'
            elif month == '7':
                monthth = 'กรกฏาคม'
            elif month == '8':
                monthth = 'สิงหาคม'
            elif month == '9':
                monthth = 'กันยายน'
            elif month == '10':
                monthth = 'ตุลาคม'
            elif month == '11':
                monthth = 'พฤศจิกายน'
            else:
                monthth = 'ธันวาคม'

        year = self.year
        company_id = self.env.company

        inv_row = 3
        worksheet.write(inv_row, 0, 'เดือนภาษี', for_left_bold_no_border)
        worksheet.write(inv_row, 1, monthth, for_left_no_border)
        worksheet.write(inv_row, 3, 'ปี', for_left_bold_no_border)
        worksheet.write(inv_row, 4, year, for_left_no_border)

        inv_row += 1
        worksheet.write(inv_row, 0, 'ชื่อผู้ประกอบการ', for_left_bold_no_border)
        worksheet.write(inv_row, 1, company_id.name, for_left_no_border)
        worksheet.write(inv_row, 3, 'เลขประจำผู้เสียภาษีอากร', for_left_bold_no_border)
        worksheet.write(inv_row, 4, company_id.vat, for_left_no_border)

        inv_row += 1
        worksheet.write(inv_row, 0, 'ชื่อสถานประกอบการ', for_left_bold_no_border)
        worksheet.write(inv_row, 3, company_id.name, for_left_no_border)
        worksheet.write(inv_row, 4, 'สำนักงานใหญ่ / สาขา', for_left_bold_no_border)
        if company_id.branch_no:
            if company_id.branch_no == '00000':
                branch_no = 'สำนักงานใหญ่'
            else:
                branch_no = 'สาขา' + ' ' + company_id.branch_no
            # branch_no = company_id.branch_no if company_id.branch_no == '00000' else 'สำนักงานใหญ่'
            worksheet.write(inv_row, 4, branch_no, for_left_no_border)
        else:
            worksheet.write(inv_row, 4, 'สำนักงานใหญ่', for_left_no_border)


        inv_row += 1
        worksheet.write(inv_row, 0, 'สถานประกอบการ', for_left_bold_no_border)
        company_address = company_id.get_company_full_address_text()
        # worksheet.write(inv_row, 1,company_address , for_left_no_border)
        worksheet.merge_range('B7:C7', company_address, for_left_no_border)



        inv_row += 3
        inv_row_merge_head = inv_row + 1
        worksheet.set_row(inv_row-1, 20)
        worksheet.merge_range('A' + str(inv_row) + ':A' + str(inv_row_merge_head), "วันที่", for_center_bold_bg)
        worksheet.merge_range('B' + str(inv_row) + ':B' + str(inv_row_merge_head),"เลขที่\nInvoice No", for_center_bold_bg)
        worksheet.merge_range('C' + str(inv_row) + ':C' + str(inv_row_merge_head), "รายการ\nCustomer", for_center_bold_bg)
        worksheet.merge_range('D' + str(inv_row) + ':D' + str(inv_row_merge_head), "จำนวนชิ้น", for_center_bold_bg)
        worksheet.merge_range('E' + str(inv_row) + ':J' + str(inv_row), "ตามส่งจริง", for_center_bold_bg)
        worksheet.write('E' + str(inv_row_merge_head), 'EUR', for_center_bold_bg)
        worksheet.write('F' + str(inv_row_merge_head), 'USD', for_center_bold_bg)
        worksheet.write('G' + str(inv_row_merge_head), 'GBP', for_center_bold_bg)
        worksheet.write('H' + str(inv_row_merge_head), 'CNY', for_center_bold_bg)
        worksheet.write('I' + str(inv_row_merge_head), 'THB', for_center_bold_bg)
        worksheet.write('J' + str(inv_row_merge_head), 'Other', for_center_bold_bg)
        worksheet.merge_range('K' + str(inv_row) + ':K' + str(inv_row_merge_head), "EXC RATE", for_center_bold_bg)
        worksheet.merge_range('L' + str(inv_row) + ':L' + str(inv_row_merge_head), "BAHT", for_center_bold_bg)
        worksheet.merge_range('M' + str(inv_row) + ':M' + str(inv_row_merge_head), "ตามใบขน\nEUR/USD", for_center_bold_bg)
        worksheet.merge_range('N' + str(inv_row) + ':N' + str(inv_row_merge_head), "EXC RATE", for_center_bold_bg)
        worksheet.merge_range('O' + str(inv_row) + ':O' + str(inv_row_merge_head), "BAHT", for_center_bold_bg)
        worksheet.merge_range('P' + str(inv_row) + ':P' + str(inv_row_merge_head), "เลขที่ใบขน", for_center_bold_bg)
        worksheet.merge_range('Q' + str(inv_row) + ':Q' + str(inv_row_merge_head), "ETD", for_center_bold_bg)
        worksheet.merge_range('R' + str(inv_row) + ':R' + str(inv_row_merge_head), "ETA", for_center_bold_bg)



        data = {}
        # data = self.read(['date_from', 'date_to', 'month', 'year', 'report_type', 'tax_id', 'company_id'])[0]
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type, 'tax_id': self.tax_id.id, 'company_id': self.company_id,'vat_0':self.vat_0,'customer':self.cuctomer.name}

        if self.report_type == 'sale':
            report_values = self.env['report.PJD_report.sale_tax_report_id2']._get_report_values(self,
                                                                                                            data=data)
            print('report_values : ', report_values)
            invoice_ids = {}
            invoices = report_values.get('docs')
            # for invoice_id in invoices:
            #     print('invoice_id:',invoice_id)
            #     # invoice_ids={
            #     #     'date': invoices
            #     # }
            print('report_values : ', report_values)
            chack = str(self.date_from).split('-')[0]
            if chack == '1902':
                print("Log:", report_values)
                # raise UserError(str(report_values))
                mess="Data :\n"
                for i in report_values['docs']:
                    mess =mess+str(i)+"\n"
                mess += "By : ["+str(self.env.user.name)+"] At : ["+str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+"]"
                raise UserError(mess)

            if self.tax_id.tax_report:
                worksheet.merge_range('A1:I1',company_id.name , for_center_bold_no_border)
                worksheet.merge_range('A2:I2', "รายการส่งออกประจำเดือน", for_center_bold_no_border)
            else:
                worksheet.merge_range('A1:I1',company_id.name, for_center_bold_no_border)
                worksheet.merge_range('A2:I2', "รายการส่งออกประจำเดือน", for_center_bold_no_border)
            amount_untaxed = 0
            amount_vat = 0
            amount_total = 0
            print('invoices:',invoices)
            if invoices:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                for inv in invoices:
                    if len(self.cuctomer)>=1:
                        if self.cuctomer.name == inv['partner']:
                            inv_row += 1
                            worksheet.write(inv_row, 0, inv['date'].strftime("%d/%m/%Y") or '', for_center_date)
                            worksheet.write(inv_row, 1, inv['name'], for_center)
                            worksheet.write(inv_row, 2, inv['partner'], for_left)
                            worksheet.write(inv_row, 3, inv['quantity'], for_center)
                            worksheet.write(inv_row, 4, "", for_center)
                            worksheet.write(inv_row, 5, "", for_center)
                            worksheet.write(inv_row, 6, "", for_center)
                            worksheet.write(inv_row, 7, "", for_center)
                            worksheet.write(inv_row, 8, "", for_center)
                            worksheet.write(inv_row, 9, "", for_center)
                            if inv['amount_type']=='EUR':
                                worksheet.write(inv_row, 4, inv['amount_total'], for_right)
                            if inv['amount_type']=='USD':
                                worksheet.write(inv_row, 5, inv['amount_total'], for_right)
                            if inv['amount_type']=='GBP':
                                worksheet.write(inv_row, 6, inv['amount_total'], for_right)
                            if inv['amount_type']=='CNY':
                                worksheet.write(inv_row, 7, inv['amount_total'], for_right)
                            if inv['amount_type']=='THB':
                                worksheet.write(inv_row, 8, inv['amount_total'], for_right)
                                worksheet.write(inv_row, 11, inv['amount_total'], for_right)
                                worksheet.write(inv_row, 10, "", for_center)
                                worksheet.write(inv_row, 14, inv['amount_total'], for_right)
                            if inv['amount_type']!='THB' and inv['amount_type'] != 'CNY' and inv['amount_type'] != 'GBP' and inv['amount_type'] != 'USD' and inv['amount_type'] != 'EUR':
                                worksheet.write(inv_row, 9, inv['amount_total'], for_right)
                            if inv['amount_type'] != 'THB':
                                company_rate_to_baht1 = inv['amount_total'] * inv['company_rate']
                                company_rate_to_baht2 = inv['amount_total'] * inv['excrate']
                                worksheet.write(inv_row, 11, company_rate_to_baht1, for_right)
                                worksheet.write(inv_row, 10, inv['company_rate'], for_right)
                                worksheet.write(inv_row, 14, company_rate_to_baht2, for_right)
                            worksheet.write(inv_row, 12, inv['amount_total'], for_right)
                            worksheet.write(inv_row, 13, inv['excrate'], for_right)
                            worksheet.write(inv_row, 15, inv['export_products_id']or'', for_center)
                            worksheet.write(inv_row, 16, inv['ETD'] or '', for_center_date)
                            worksheet.write(inv_row, 17, inv['ETA'] or '', for_center_date)
                    if len(self.cuctomer) < 1:
                        inv_row += 1
                        worksheet.write(inv_row, 0, inv['date'] or '', for_center_date)
                        worksheet.write(inv_row, 1, inv['name'], for_center)
                        worksheet.write(inv_row, 2, inv['partner'], for_left)
                        worksheet.write(inv_row, 3, inv['quantity'], for_center)
                        worksheet.write(inv_row, 4, "", for_center)
                        worksheet.write(inv_row, 5, "", for_center)
                        worksheet.write(inv_row, 6, "", for_center)
                        worksheet.write(inv_row, 7, "", for_center)
                        worksheet.write(inv_row, 8, "", for_center)
                        worksheet.write(inv_row, 9, "", for_center)
                        if inv['amount_type'] == 'EUR':
                            worksheet.write(inv_row, 4, inv['amount_total'], for_right)
                        if inv['amount_type'] == 'USD':
                            worksheet.write(inv_row, 5, inv['amount_total'], for_right)
                        if inv['amount_type'] == 'GBP':
                            worksheet.write(inv_row, 6, inv['amount_total'], for_right)
                        if inv['amount_type'] == 'CNY':
                            worksheet.write(inv_row, 7, inv['amount_total'], for_right)
                        if inv['amount_type'] == 'THB':
                            worksheet.write(inv_row, 8, inv['amount_total'], for_right)
                            worksheet.write(inv_row, 11, inv['amount_total'], for_right)
                            worksheet.write(inv_row, 10, "", for_center)
                            worksheet.write(inv_row, 14, inv['amount_total'], for_right)
                        if inv['amount_type'] != 'THB' and inv['amount_type'] != 'CNY' and inv[
                            'amount_type'] != 'GBP' and inv['amount_type'] != 'USD' and inv['amount_type'] != 'EUR':
                            worksheet.write(inv_row, 9, inv['amount_total'], for_right)
                        if inv['amount_type'] != 'THB':
                            company_rate_to_baht1 = inv['amount_total'] * inv['company_rate']
                            company_rate_to_baht2 = inv['amount_total'] * inv['excrate']
                            worksheet.write(inv_row, 11, company_rate_to_baht1, for_right)
                            worksheet.write(inv_row, 10, inv['company_rate'], for_right)
                            worksheet.write(inv_row, 14, company_rate_to_baht2, for_right)
                        worksheet.write(inv_row, 12, inv['amount_total'], for_right)
                        worksheet.write(inv_row, 13, inv['excrate'], for_right)
                        worksheet.write(inv_row, 15, inv['export_products_id'] or '', for_center)
                        worksheet.write(inv_row, 16, inv['ETD'] or '', for_center_date)
                        worksheet.write(inv_row, 17, inv['ETA'] or '', for_center_date)


        else:
            report_values = self.env['report.PJD_report.purchase_tax_report_id2']._get_report_values(self,data=data)
            move_lines = report_values.get('docs')
            print('move_lines : ', move_lines)

            if self.tax_id.tax_report:
                worksheet.merge_range('A1:I1', "รายการส่งออกประจำเดือน", for_center_bold_no_border)
            else:
                worksheet.merge_range('A1:I1', "รายการส่งออกประจำเดือน", for_center_bold_no_border)
            amount_total = 0
            before_total = 0
            amount_tax_total = 0
            if move_lines:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                amount_tax = amount_untax = 0.0
                for ml in move_lines:
                    print('ml:',ml)
                    inv_row += 1
                    worksheet.write(inv_row, 0, sl_no, for_center)

                    worksheet.write(inv_row, 1, ml['date'] or '', for_center_date)

                    worksheet.write(inv_row, 2, ml['ref'], for_left)
                    worksheet.write(inv_row, 3, ml['partner'].name, for_left)
                    worksheet.write(inv_row, 4, ml['vat'], for_left)
                    if ml['branch'] == '00000':
                        worksheet.write(inv_row, 5, ml['branch'], for_right)
                        worksheet.write(inv_row, 6, '', for_left)
                    else:
                        worksheet.write(inv_row, 5, ' ', for_left)
                        worksheet.write(inv_row, 6, ml['branch'], for_right)
                    if ml['debit']:
                        amount_tax = ml['debit']
                    elif ml['credit']:
                        amount_tax = ml['credit']
                    else:
                        amount_tax = 0

                    if ml['amount_untaxed']:
                        if ml['type'] == 'in_refund':
                            if ml['amount_untaxed'] > 0:
                                amount_untax = ml['amount_untaxed'] * (-1)
                            else:
                                amount_untax = ml['amount_untaxed']
                        else:
                            amount_untax = ml['amount_untaxed']
                    else:
                        amount_untax = amount_tax * 100 / 7

                    if ml['type'] == 'in_refund':
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                            else:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                                before_total += amount_untax
                        else:
                            if ml['debit']:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                            else:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                    else:
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                            else:
                                worksheet.write(inv_row, 7, '0.00', for_right_border_num_format)
                                before_total += amount_untax
                        else:
                            if ml['debit']:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax
                            else:
                                worksheet.write(inv_row, 7, amount_untax, for_right_border_num_format)
                                before_total += amount_untax


                    if ml['type'] == 'in_refund':
                        if ml['state'] == 'cancel':
                            if ml['debit']:
                                debit_credit = ml['debit']
                            elif ml['credit']:
                                debit_credit = ml['credit']
                            worksheet.write(inv_row, 8, '0.00', for_right_border_num_format)
                            worksheet.write(inv_row, 9, '0.00', for_right_border_num_format)
                            amount_total += '0.00' + amount_untax
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                        else:
                            if ml['debit']:
                                debit_credit = ml['debit']
                            elif ml['credit']:
                                debit_credit = ml['credit']
                            worksheet.write(inv_row, 8, ml['debit'] or ml['credit'] * (-1), for_right_border_num_format)
                            worksheet.write(inv_row, 9, (debit_credit * (-1) + amount_untax), for_right_border_num_format)
                            amount_total += (debit_credit * (-1)) + amount_untax
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                            worksheet.write(inv_row, 10, ml['note'], for_right)

                    else:
                        if ml['state'] == 'cancel':
                            worksheet.write(inv_row, 8,'0.00', for_right_border_num_format)
                            worksheet.write(inv_row, 9, '0.00',for_right_border_num_format)
                            worksheet.write(inv_row, 10, 'ยกเลิก (Cancel)', for_right)
                        else:
                            worksheet.write(inv_row, 8, ml['debit'] or ml['credit'], for_right_border_num_format)
                            worksheet.write(inv_row, 9, ml['debit'] + ml['credit'] + amount_untax,for_right_border_num_format)
                            amount_total += ml['debit'] + ml['credit'] + amount_untax
                            worksheet.write(inv_row, 10, ml['note'], for_right)

                    sl_no += 1
                    if ml['type'] == 'in_refund':
                        if ml['state'] != 'cancel':
                            amount_tax_total += ml['debit'] * (-1)
                            amount_tax_total += ml['credit'] * (-1)
                    else:
                        if ml['state'] != 'cancel':
                            amount_tax_total += ml['debit']
                            amount_tax_total += ml['credit']

                inv_row += 1
                worksheet.write(inv_row, 6, 'Total', for_center_bold)
                worksheet.write(inv_row, 7, before_total, for_right_bold_border_num_format)
                worksheet.write(inv_row, 8, amount_tax_total, for_right_bold_border_num_format)
                worksheet.write(inv_row, 9, amount_total , for_right_bold_border_num_format)


        workbook.close()
        buf = fl.getvalue()
        # vals = {'name': namexls, 'report_file': base64.encodestring(buf)}
        vals = {'name': namexls, 'report_file': base64.encodebytes(buf)}
        self._cr.execute("TRUNCATE tax_excel_export2 CASCADE")
        wizard_id = self.env['tax.excel.export2'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.excel.export2',
            'target': 'new',
            'res_id': wizard_id.id,
        }


class tax_excel_export2(models.TransientModel):
    _name = 'tax.excel.export2'

    report_file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    # @api.model
    # def create(self, vals):
    #     print vals
    #     return super(tax_excel_export, self).create(vals)

    # @api.multi
    def action_back(self):
        if self._context is None:
            self._context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.report',
            'target': 'new',
        }

