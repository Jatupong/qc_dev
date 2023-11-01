# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import tempfile
import binascii
from datetime import datetime, date
import xlrd

from odoo import fields, models, _
from odoo.exceptions import UserError
from io import BytesIO
import xlsxwriter
from dateutil.relativedelta import relativedelta

# from datetime import date

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class product_purchase_report(models.TransientModel):
    # return_card_report
    # _name = "return.card.report"
    _name = "product.purchase.report"


    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    warehouse = fields.Many2one(string="Warehouse", comodel_name='stock.warehouse')
    location = fields.Many2one(string="Location", comodel_name='stock.location')

    category_id = fields.Many2one(string='Category',comodel_name='product.category')
    product = fields.Many2one(string='Product',comodel_name='product.template')


    def print_report_excel(self):
        [data] = self.read()
        datas = {'form': data}

        str2d = fields.Date.from_string
        date_from = str2d(self.date_from)
        date_to = str2d(self.date_to)
        # date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        # date_to_obj = datetime.strptime(self.date_from, '%Y-%m-%d')
        report_file = "po" + str(date_from.strftime("%d/%m/%Y")) + "-" + str(date_to.strftime("%d/%m/%Y"))
        self.env.ref('product_purchase_report_excel_export').report_file = report_file

        return self.env.ref('product_purchase_report_excel_export').report_action(self, data=datas, config=False)


    def get_without_analytic_line_ids(self):
        domain = [('move_type', 'in', ('in_invoice', 'in_refund')),
                  ('invoice_date', '>=', self.date_from),
                  ('invoice_date', '<=', self.date_to),
                  ('product_id', '!=', False),
                  ]
        if self.vendors_id:
            domain += [('partner_id', '=', self.vendors_id.id)]
        if self.invoice_state:
            domain += [('move_id.state', '=', self.invoice_state)]

        move_line = self.env['account.move.line'].search(domain, order='invoice_date asc')

        return move_line

    def date_from_1(self):

        date_1 = self.date_from
        return date_1

    def date_to_1(self):

        date_1 = self.date_to
        return date_1

    def analyic_account_id_1(self):

        analyic_account_id = self.analyic_account_id
        return analyic_account_id




class product_purchase_report_excel_export(models.TransientModel):
    _name = 'product.purchase.report.excel.export'

    report_file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    def action_back(self):
        if self._context is None:
            self._context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.purchase.report',
            'target': 'new',
        }


class WizardPoReportXls(models.AbstractModel):
    _name = 'report.wizard_report_inventory'

    def generate_xlsx_report(self, workbook, data, lines):
        fl = BytesIO()
        # workbook = xlsxwriter.Workbook(fl)
        name = 'InventoryReport'
        # namexls = 'Purchase Report' + '.xls'
        worksheet = workbook.add_worksheet(name)
        # print('generate_xlsx_report product_in_report_xls')
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
        for_right = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})

        for_right_bold_no_border_date = workbook.add_format({'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0.00'})

        for_center_bold_no_border_date = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_left_bold_no_border_date = workbook.add_format({'align': 'left', 'bold': True, 'num_format': 'dd/mm/yy'})

        for_center_date = workbook.add_format({'align': 'center', 'num_format': 'dd/mm/yyyy', 'border': True})

        date1 = lines.date_from_1()
        date2 = lines.date_to_1()
        inv_row = 0

        worksheet.write(0, 6, 'Supiler', for_center_bold_no_border_date)
        # worksheet.write(0, 1, docs1.company_id.name, for_center_bold_no_border_date)

        worksheet.write(1, 4, 'ตั้งแต่วันที่', for_center_bold_no_border_date)
        worksheet.write(1, 5, date1, for_center_bold_no_border_date)
        worksheet.write(1, 6, 'ถึง', for_center_bold_no_border_date)
        worksheet.write(1, 7, date2, for_center_bold_no_border_date)

        worksheet.write(3, 0, 'วัน / เดือน / ปี', for_center_bold)
        worksheet.write(3, 1, 'รหัสเจ้าหนี้', for_center_bold)
        worksheet.write(3, 2, 'ชื่อเจ้าหนี้', for_center_bold)
        worksheet.write(3, 3, 'เลขที่ invoice', for_center_bold)
        worksheet.write(3, 4, 'เลขอ้างอิง', for_center_bold)
        worksheet.write(3, 5, 'Supplier Invoice', for_center_bold)
        worksheet.write(3, 6, 'Analytic account', for_center_bold)
        worksheet.write(3, 7, 'รห้สสินค้า', for_center_bold)
        worksheet.write(3, 8, 'ชื่อสินค้า', for_center_bold)
        worksheet.write(3, 9, 'Description', for_center_bold)
        worksheet.write(3, 10, 'Unit', for_center_bold)
        worksheet.write(3, 11, 'ราคาต่อหน่วย', for_center_bold)
        worksheet.write(3, 12, 'จำนวน', for_center_bold)
        worksheet.write(3, 13, 'ราคา', for_center_bold)
        worksheet.write(3, 14, 'ภาษี', for_center_bold)
        worksheet.write(3, 15, 'ผลรวมทั้งหมด', for_center_bold)

        inv_col = 0
        inv_row = 4
        count = 1
        sum_1 = 0.0
        sum_2 = 0.0
        sum_3 = 0.0
        price_tax = 0.0

        move_lines = lines.get_without_analytic_line_ids()
        if not move_lines:
            raise UserError(_("Document is empty."))
        for move_line in move_lines:
            move_line_id = move_line
            invoice_id = move_line.move_id
            print('invoice_id.name', invoice_id.name)
            print('analytic_line_ids', move_line.analytic_line_ids)
            print('analytic_distribution', move_line.analytic_distribution)
            if move_line.analytic_distribution:
                for line in move_line.analytic_distribution:
                    analyic_account_id = lines.analyic_account_id_1()
                    # if self.analyic_account_id and self.analyic_account_id != int(line):
                    if analyic_account_id and analyic_account_id != int(line):
                        pass
                    account_id = self.env['account.analytic.account'].browse(int(line))
                    worksheet.write(inv_row, inv_col, invoice_id.invoice_date, for_center_date)
                    # print('account_id ', account_id.name)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, invoice_id.partner_id.ref or '', for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, invoice_id.partner_id.name, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, invoice_id.name, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.purchase_order_id.name or '', for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, invoice_id.ref or '', for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, account_id.name, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.product_id.default_code or '', for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.product_id.name or '', for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.name, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.product_uom_id.name, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.price_unit, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.quantity, for_left)
                    inv_col += 1
                    worksheet.write(inv_row, inv_col, move_line_id.price_subtotal, for_right_border_num_format)
                    sum_1 += move_line_id.price_subtotal
                    inv_col += 1
                    tax_line = move_line_id.price_subtotal * 0.07
                    # worksheet.write(inv_row, inv_col, i1.tax_ids.name, for_center_bold)
                    worksheet.write(inv_row, inv_col, tax_line, for_right_border_num_format)
                    sum_2 += tax_line
                    inv_col += 1
                    price_tax = move_line_id.price_subtotal + tax_line
                    # worksheet.write(inv_row, inv_col, i1.price_subtotal, for_center_bold)
                    worksheet.write(inv_row, inv_col, price_tax, for_right_border_num_format)
                    sum_3 = sum_3 + price_tax
                    inv_row += 1
                    inv_col = 0
            # elif not self.analyic_account_id:
            elif not analyic_account_id:
                # else:
                worksheet.write(inv_row, inv_col, invoice_id.invoice_date, for_center_date)
                inv_col += 1
                worksheet.write(inv_row, inv_col, invoice_id.partner_id.ref or '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, invoice_id.partner_id.name, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, invoice_id.name, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.purchase_order_id.name or '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, invoice_id.ref or '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.product_id.default_code or '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.product_id.name or '', for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.name, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.product_uom_id.name, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.price_unit, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.quantity, for_left)
                inv_col += 1
                worksheet.write(inv_row, inv_col, move_line_id.price_subtotal, for_right_border_num_format)
                sum_1 += move_line_id.price_subtotal
                inv_col += 1
                tax_line = move_line_id.price_subtotal * 0.07
                # worksheet.write(inv_row, inv_col, i1.tax_ids.name, for_left)
                worksheet.write(inv_row, inv_col, tax_line, for_right_border_num_format)
                sum_2 += tax_line
                inv_col += 1
                price_tax = move_line_id.price_subtotal + tax_line
                # worksheet.write(inv_row, inv_col, i1.price_subtotal, for_left)
                worksheet.write(inv_row, inv_col, price_tax, for_right_border_num_format)
                sum_3 = sum_3 + price_tax

                inv_row += 1
                inv_col = 0

        worksheet.write(inv_row, 12, 'ยอดรวม', for_center_bold)
        worksheet.write(inv_row, 13, sum_1, for_right_border_num_format)
        worksheet.write(inv_row, 14, sum_2, for_right_border_num_format)
        worksheet.write(inv_row, 15, sum_3, for_right_border_num_format)

        workbook.close()
