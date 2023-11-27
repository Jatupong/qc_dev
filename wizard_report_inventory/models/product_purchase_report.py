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

    date_from = fields.Date(string='Date From', requests=True)
    date_to = fields.Date(string='Date To', requests=True)
    warehouse = fields.Many2one(string="Warehouse", comodel_name='stock.warehouse')
    location = fields.Many2one(string="Location", comodel_name='stock.location')

    category_id = fields.Many2one(string='Category', comodel_name='product.category')
    product = fields.Many2one(string='Product', comodel_name='product.template')

    # def get_detail(self):
    #     result = []
    #
    #     # test data
    #     # domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to)]
    #     # if self.operating_unit_id:
    #     #     domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
    #     #           ('picking_type_id.warehouse_id.id', '=', self.operating_unit_id.id)]
    #     # else:
    #     #     domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
    #     #              ]
    #     # docs = self.env['stock.picking'].search(domain)
    #     # com = docs.company_id.name
    #
    #     # for st in docs:
    #     number_ship_id = self.number_ship_id
    #     product_type = self.product_type
    #     product_raw_materials = self.product_raw_materials
    #     product_raw_materials_id = self.product_raw_materials_id
    #     # date_present = self.date_present
    #
    #     line1 = {
    #         'data': "0",
    #         'data1': '1',
    #         'data2': '2',
    #         'data3': '3',
    #         'data4': '4',
    #         'data5': '5',
    #         'data6': '6',
    #         'data7': '7',
    #         'data8': '8',
    #         'data9': '9',
    #         'data10': '10',
    #         'data11': '11',
    #         'data12': '12',
    #
    #
    #     }
    #
    #     result.append(line1)
    #     return result

    # def get_detail_by_branch(self):
    #     result = []
    #
    #     # test data
    #     # domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to)]
    #     if self.operating_unit_id:
    #         domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
    #               ('picking_type_id.warehouse_id.id', '=', self.operating_unit_id.id)]
    #     else:
    #         domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
    #                  ]
    #     docs = self.env['stock.picking'].search(domain)
    #     com = docs.company_id.name
    #
    #     for st in docs:
    #
    #         line1 = {
    #             'data': 'dddd',
    #             'data1': 'ssss',
    #             'data2': 'ssss',
    #             'data3': 'ssss',
    #             'data4': 'ssss',
    #             'data5': '5',
    #             'data6': '6',
    #             'data7': '7',
    #             'data8': '8',
    #             'data9': '9',
    #             'data10': '10',
    #             'data11': '11',
    #             'data12': '12',
    #
    #
    #         }
    #
    #         result.append(line1)
    #     return result

    def day_to_str(self, date_from):
        Date = str(date_from).split("-")
        print(Date)
        year = int(Date[0]) + 543
        month = int(Date[1])
        day = int(Date[2])

        # def day_to_str(self, date_from, date_to):
        #     Date = str(date_from).split("-")
        #     print(Date)
        #     year = int(Date[0]) + 543
        #     month = int(Date[1])
        #     day = int(Date[2])

        # if month:
        #     if month == 1:
        #         monthth = 'มกราคม'
        #     elif month == 2:
        #         monthth = 'กุมภาพันธ์'
        #     elif month == 3:
        #         monthth = 'มีนาคม'
        #     elif month == 4:
        #         monthth = 'เมษายน'
        #     elif month == 5:
        #         monthth = 'พฤษภาคม'
        #     elif month == 6:
        #         monthth = 'มิถุนายน'
        #     elif month == 7:
        #         monthth = 'กรกฏาคม'
        #     elif month == 8:
        #         monthth = 'สิงหาคม'
        #     elif month == 9:
        #         monthth = 'กันยายน'
        #     elif month == 10:
        #         monthth = 'ตุลาคม'
        #     elif month == 11:
        #         monthth = 'พฤศจิกายน'
        #     else:
        #         monthth = 'ธันวาคม'

        if month:
            if month == 1:
                monthth = '01'
            elif month == 2:
                monthth = '02'
            elif month == 3:
                monthth = '03'
            elif month == 4:
                monthth = '04'
            elif month == 5:
                monthth = '05'
            elif month == 6:
                monthth = '06'
            elif month == 7:
                monthth = '07'
            elif month == 8:
                monthth = '08'
            elif month == 9:
                monthth = '09'
            elif month == 10:
                monthth = '10'
            elif month == 11:
                monthth = '11'
            else:
                monthth = '12'

        print(day, monthth, year)
        return day, monthth, year

        # for q in moves_layer:
        #     qty = 0
        #     for Zum in q.valuation.layer:
        #         qty += Zum.q.quantity
        #         print('qty', qty)
        #
        # for v in moves_layer:
        #     value = 0
        #     for Zum in v.valuation.layer:
        #         value += Zum.v.value

    def print_report_excel(self):
        print('print_report_xls')
        fl = BytesIO()
        workbook = xlsxwriter.Workbook(fl)
        name = 'Product purchase report'
        namexls = 'Product purchase report' + '.xls'
        worksheet = workbook.add_worksheet(name)
        company = self.env.company

        for_left_bold_no_border = workbook.add_format({'align': 'left', 'bold': True})
        for_center_bold_no_border = workbook.add_format({'align': 'center', 'bold': True})
        for_right_bold_no_border = workbook.add_format({'align': 'right', 'bold': True})

        for_left_no_border = workbook.add_format({'align': 'left'})
        for_left_border = workbook.add_format({'align': 'left', 'border': True})
        for_center_no_border = workbook.add_format({'align': 'center'})
        for_center_border = workbook.add_format({'align': 'center', 'border': True})
        for_right_no_border = workbook.add_format({'align': 'right'})

        for_left_bold = workbook.add_format({'align': 'left', 'bold': True, 'border': True})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True, 'border': True})
        for_right_bold = workbook.add_format({'align': 'right', 'bold': True, 'border': True})
        for_center_bold_bg = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': True, 'bg_color': '#ffff'})
        for_right_bold = workbook.add_format({'align': 'right', 'bold': True, 'border': True})
        for_right_bold_bg = workbook.add_format({'align': 'right', 'bold': True, 'border': True, 'bg_color': '#FFFF00'})
        for_right_bold_bg_no_border_left_right = workbook.add_format({
            'align': 'right',
            'bold': True,
            'border': True,
            'bg_color': '#FFFF00',
            'top': True,  # เปิดเส้นขอบด้านบน
            'bottom': True,  # เปิดเส้นขอบด้านล่าง
            'left': False,  # ปิดเส้นขอบด้านซ้าย
            'right': False  # ปิดเส้นขอบด้านขวา
        })
        for_right_bold_bg_no_border_right = workbook.add_format({
            'align': 'right',
            'bold': True,
            'border': True,
            'bg_color': '#FFFF00',
            'top': True,
            'bottom': True,
            'left': False,
            'right': True
        })

        for_left = workbook.add_format({'align': 'left', 'border': True})
        for_center = workbook.add_format({'align': 'center', 'border': True})
        for_right = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})

        for_right_bold_no_border_date = workbook.add_format(
            {'align': 'right', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_right_border_num_format = workbook.add_format(
            {'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0.00'})

        for_center_bold_no_border_date = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_center_border_date = workbook.add_format(
            {'align': 'center', 'bold': False, 'border': True, 'num_format': 'dd/mm/yy'})
        for_left_bold_no_border_date = workbook.add_format(
            {'align': 'left', 'bold': True, 'num_format': 'dd/mm/yy'})

        for_center_date = workbook.add_format({'align': 'center', 'border': False, 'num_format': 'dd/mm/yyyy'})

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 25)
        worksheet.set_column('Q:Q', 20)
        worksheet.set_column('R:R', 20)
        worksheet.set_column('S:S', 25)

        inv_row = 1
        worksheet.merge_range('A' + str(inv_row) + ':I' + str(inv_row), 'รายงานการซื้อสินค้า', for_center_bold)

        inv_row += 1
        day, monthth, year = self.day_to_str(date.today())
        worksheet.merge_range('A' + str(inv_row) + ':I' + str(inv_row),
                              "ข้อมูลวันที่ {} - {}".format(self.date_from, self.date_to), for_center_bold)

        inv_row += 2
        worksheet.write('D' + str(inv_row), "คลังสินค้า", for_center_bold)
        worksheet.write('E' + str(inv_row), self.location.name or '', for_center_bold)
        inv_row += 1
        worksheet.write('D' + str(inv_row), "Catergory", for_center_bold)
        worksheet.write('E' + str(inv_row), self.category_id.name or '', for_center_bold)
        inv_row += 1
        worksheet.write('D' + str(inv_row), "สินค้า", for_center_bold)
        worksheet.write('E' + str(inv_row), self.product.name or '', for_center_bold)

        inv_row += 2
        worksheet.merge_range('A' + str(inv_row) + ':G' + str(inv_row), " ", for_center_bold)
        worksheet.merge_range('H' + str(inv_row) + ':I' + str(inv_row), "ยอด", for_center_bold)

        inv_row += 1
        header = ["Suppiler", "วันที่เข้ารับ", "Picking Number", "วันที่ตาม PO", "เลขที่อ้างอิง", "Bills", "Lot",
                  "จำนวน", "มูลค่า"]
        Col = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S"]
        # haeder
        worksheet.set_row(inv_row - 1, 20)
        for i in range(len(header)):
            try:
                worksheet.write(str(Col[i]) + str(inv_row), header[i], for_center_bold)
            except:
                worksheet.write(str(Col[i]) + str(inv_row), "", for_center_bold)
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------

        domain = [('scheduled_date', '>=', self.date_from), ('scheduled_date', '<=', self.date_to)
                  ]
        if len(self.warehouse) >= 1:
            domain += [('location_id', '=', self.warehouse)]
        if len(self.location) >= 1:
            domain += [('location_id.name', '=', self.location.name)]
        # if len(self.product.name)>= 1:
        #     domain += [('product_id.name', '=', self.product.name)]

        sum_unit = 0.0
        sum_price = 0.0
        Stocks = self.env['stock.picking'].search(domain)
        print(Stocks.sorted(key=lambda x: str(x.partner_id.name)))
        for stock in Stocks.sorted(key=lambda x: str(x.partner_id.name)):

            if self.product.name != False and stock.product_id.name == self.product.name:

                if 'P0' in str(stock.group_id.name) and 'IN' in str(stock.name).split('/'):
                    print(stock.product_id.name)
                    worksheet.write(inv_row, 0, stock.partner_id.name or ' ', for_center)
                    worksheet.write(inv_row, 1, stock.scheduled_date or ' ', for_center_border_date)
                    worksheet.write(inv_row, 2, stock.name or ' ', for_center)
                    worksheet.write(inv_row, 3, stock.date_done or ' ', for_center_border_date)
                    worksheet.write(inv_row, 4, stock.group_id.name or ' ', for_center)

                    domain = [("invoice_origin", "=", stock.origin)]
                    move_bill = self.env['account.move'].search(domain)
                    for bill in move_bill:
                        worksheet.write(inv_row, 5, bill.name or ' ', for_center)
                    for line in stock.move_line_nosuggest_ids:
                        worksheet.write(inv_row, 6, line.lot_id.name or ' ', for_center)
                        worksheet.write(inv_row, 7, line.qty_done or ' ', for_right_border_num_format)
                        domainp = [("product_id.name", "=", stock.product_id.name), ("reference", "=", stock.name),("quantity", "=", line.qty_done)]
                        Unit_cost = self.env['stock.valuation.layer'].search(domainp)
                        if len(Unit_cost)>=2:
                            Unit_cost = Unit_cost[0]
                        worksheet.write(inv_row, 8, line.qty_done * Unit_cost.unit_cost or ' ',
                                        for_right_border_num_format)
                        sum_unit += line.qty_done
                        sum_price += line.qty_done * Unit_cost.unit_cost
                        inv_row += 1
                        worksheet.write(inv_row, 0, ' ', for_center)
                        worksheet.write(inv_row, 1, ' ', for_center_border_date)
                        worksheet.write(inv_row, 2, ' ', for_center)
                        worksheet.write(inv_row, 3, ' ', for_center_border_date)
                        worksheet.write(inv_row, 4, ' ', for_center)
                        worksheet.write(inv_row, 5, ' ', for_center)
            if self.product.name == False:
                print(stock.product_id.name)
                if 'P0' in str(stock.group_id.name) and 'IN' in str(stock.name).split('/'):
                    worksheet.write(inv_row, 0, stock.partner_id.name or ' ', for_center)
                    worksheet.write(inv_row, 1, stock.scheduled_date or ' ', for_center_border_date)
                    worksheet.write(inv_row, 2, stock.name or ' ', for_center)
                    worksheet.write(inv_row, 3, stock.date_done or ' ', for_center_border_date)
                    worksheet.write(inv_row, 4, stock.group_id.name or ' ', for_center)

                    domain = [("invoice_origin", "=", stock.origin)]
                    move_bill = self.env['account.move'].search(domain)
                    for bill in move_bill:
                        worksheet.write(inv_row, 5, bill.name or ' ', for_center)
                    for line in stock.move_line_nosuggest_ids:
                        worksheet.write(inv_row, 6, line.lot_id.name or ' ', for_center)
                        worksheet.write(inv_row, 7, line.qty_done or ' ', for_right_border_num_format)
                        domainp = [("product_id.name", "=", stock.product_id.name), ("reference", "=", stock.name),("quantity", "=", line.qty_done)]
                        Unit_cost = self.env['stock.valuation.layer'].search(domainp)
                        if len(Unit_cost)>=2:
                            Unit_cost = Unit_cost[0]
                        worksheet.write(inv_row, 8, line.qty_done * Unit_cost.unit_cost or ' ',
                                        for_right_border_num_format)
                        sum_unit += line.qty_done
                        sum_price += line.qty_done * Unit_cost.unit_cost
                        inv_row += 1
                        worksheet.write(inv_row, 0, ' ', for_center)
                        worksheet.write(inv_row, 1, ' ', for_center_border_date)
                        worksheet.write(inv_row, 2, ' ', for_center)
                        worksheet.write(inv_row, 3, ' ', for_center_border_date)
                        worksheet.write(inv_row, 4, ' ', for_center)
                        worksheet.write(inv_row, 5, ' ', for_center)

        inv_row += 1
        worksheet.merge_range('A' + str(inv_row) + ':G' + str(inv_row),"รวม", for_right_bold)
        worksheet.write(inv_row-1, 7, sum_unit or '', for_right_border_num_format)
        worksheet.write(inv_row-1, 8,sum_price or '' , for_right_border_num_format)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------

        workbook.close()
        buf = fl.getvalue()
        vals = {'name': namexls, 'report_file': base64.encodebytes(buf)}
        self._cr.execute("TRUNCATE product_purchase_report_excel_export CASCADE")
        wizard_id = self.env['product.purchase.report.excel.export'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.purchase.report.excel.export',
            'target': 'new',
            'res_id': wizard_id.id,
        }


# ---------------------------------------------------------------------------------------------------------------------------------------------------------

class product_purchase_report_excel_export(models.TransientModel):
    # return_card_report_excel_export
    # _name = 'return.card.report.excel.export'
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
