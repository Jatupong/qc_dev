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


class return_card_report(models.TransientModel):
    _name = "return.card.report"

    category_id = fields.Many2one(string='Category',comodel_name='product.category')
    product = fields.Many2one(string='Product',comodel_name='product.template')
    location = fields.Many2one(string="Location", comodel_name='stock.location')
    warehouse = fields.Many2one(string="Warehouse", comodel_name='stock.location')
    date_present = fields.Date('Date',default=datetime.today().date())

    # type = fields.Selection([('off_line', 'Offline'),
    #                          ('on_line', 'Online'),
    #                          ],required=1,string='Type')

    def get_detail(self):
        result = []

        # test data
        # domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to)]
        # if self.operating_unit_id:
        #     domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
        #           ('picking_type_id.warehouse_id.id', '=', self.operating_unit_id.id)]
        # else:
        #     domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
        #              ]
        # docs = self.env['stock.picking'].search(domain)
        # com = docs.company_id.name

        # for st in docs:
        number_ship_id = self.number_ship_id
        product_type = self.product_type
        product_raw_materials = self.product_raw_materials
        product_raw_materials_id = self.product_raw_materials_id
        date_present = self.date_present

        line1 = {
            'data': number_ship_id,
            'data1': product_type,
            'data2': product_raw_materials,
            'data3': product_raw_materials_id,
            'data4': date_present,
            'data5': '5',
            'data6': '6',
            'data7': '7',
            'data8': '8',
            'data9': '9',
            'data10': '10',
            'data11': '11',
            'data12': '12',


        }

        result.append(line1)
        return result


    def get_detail_by_branch(self):
        result = []

        # test data
        # domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to)]
        if self.operating_unit_id:
            domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
                  ('picking_type_id.warehouse_id.id', '=', self.operating_unit_id.id)]
        else:
            domain = [('date_done', '>=', self.date_from), ('date_done', '<=', self.date_to),
                     ]
        docs = self.env['stock.picking'].search(domain)
        com = docs.company_id.name

        for st in docs:

            line1 = {
                'data': 'dddd',
                'data1': 'ssss',
                'data2': 'ssss',
                'data3': 'ssss',
                'data4': 'ssss',
                'data5': '5',
                'data6': '6',
                'data7': '7',
                'data8': '8',
                'data9': '9',
                'data10': '10',
                'data11': '11',
                'data12': '12',


            }

            result.append(line1)
        return result

    def day_to_str(self,date_present):
        Date = str(date_present).split("-")
        print(Date)
        year = int(Date[0]) + 543
        month = int(Date[1])
        day = int(Date[2])

        if month:
            if month == 1:
                monthth = 'มกราคม'
            elif month == 2:
                monthth = 'กุมภาพันธ์'
            elif month == 3:
                monthth = 'มีนาคม'
            elif month == 4:
                monthth = 'เมษายน'
            elif month == 5:
                monthth = 'พฤษภาคม'
            elif month == 6:
                monthth = 'มิถุนายน'
            elif month == 7:
                monthth = 'กรกฏาคม'
            elif month == 8:
                monthth = 'สิงหาคม'
            elif month == 9:
                monthth = 'กันยายน'
            elif month == 10:
                monthth = 'ตุลาคม'
            elif month == 11:
                monthth = 'พฤศจิกายน'
            else:
                monthth = 'ธันวาคม'

        print(day, monthth, year)
        return day, monthth, year

    def print_report_excel(self):
        print('print_report_xls')
        fl = BytesIO()
        workbook = xlsxwriter.Workbook(fl)
        name = 'รายงานสินค้าคงคลังสำหรับกรมศุล'
        namexls = 'รายงานสินค้าคงคลังกรมศุล' + '.xls'
        worksheet = workbook.add_worksheet(name)
        company = self.env.company

        for_left_bold_no_border = workbook.add_format({'align': 'left', 'bold': True})
        for_center_bold_no_border = workbook.add_format({'align': 'center', 'bold': True})
        for_right_bold_no_border = workbook.add_format({'align': 'right', 'bold': True})

        for_left_no_border = workbook.add_format({'align': 'left'})
        for_left_border = workbook.add_format({'align': 'left','border': True})
        for_center_no_border = workbook.add_format({'align': 'center'})
        for_center_border = workbook.add_format({'align': 'center','border': True})
        for_right_no_border = workbook.add_format({'align': 'right'})

        for_left_bold = workbook.add_format({'align': 'left', 'bold': True, 'border': True})
        for_center_bold = workbook.add_format({'align': 'center', 'bold': True, 'border': True})
        for_center_bold_bg = workbook.add_format({'align': 'center','valign': 'vcenter', 'bold': True, 'border': True, 'bg_color': '#E1F5FE'})
        for_right_bold = workbook.add_format({'align': 'right', 'bold': True, 'border': True})

        for_left = workbook.add_format({'align': 'left', 'border': True})
        for_center = workbook.add_format({'align': 'center', 'border': True})
        for_right = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})

        for_right_bold_no_border_date = workbook.add_format({'align': 'right', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_right_border_num_format = workbook.add_format({'align': 'right', 'border': True, 'num_format': '#,##0.00'})
        for_right_bold_border_num_format = workbook.add_format(
            {'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0.00'})

        for_center_bold_no_border_date = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': 'dd/mm/yy'})
        for_center_border_date = workbook.add_format(
            {'align': 'center', 'bold': False, 'border': True,  'num_format': 'dd/mm/yy'})
        for_left_bold_no_border_date = workbook.add_format({'align': 'left', 'bold': True, 'num_format': 'dd/mm/yy'})

        for_center_date = workbook.add_format({'align': 'center', 'border': False,  'num_format': 'dd/mm/yyyy'})

        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 40)
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
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)

        domain = []
        if self.category_id.complete_name != False:
            domain += [('categ_id', '=', self.category_id.complete_name)]
            # print(domain)
        if self.product.name != False:
            domain += [('name', '=', self.product.name)]
            # print(domain)
        Stocks = self.env['product.product'].search(domain)
        # print(Stocks)


        inv_row = 1
        worksheet.merge_range('A' + str(inv_row) + ':J' + str(inv_row), company.name, for_center_bold_no_border)
        inv_row +=1
        worksheet.merge_range('A' + str(inv_row) + ':J' + str(inv_row), "รายงานของคงเหลือ", for_center_bold_no_border)
        inv_row += 1
        day, monthth, year = self.day_to_str(date.today())
        worksheet.merge_range('A' + str(inv_row) + ':J' + str(inv_row), "ณ วันที่ {} {} พ.ศ.{}".format(day,monthth,year), for_center_bold_no_border)

        inv_row += 3
        worksheet.set_row(inv_row-1, 40)
        worksheet.write('A' + str(inv_row), "ลำดับที่", for_center_bold_bg)
        worksheet.write('B' + str(inv_row), "เลขที่ใบขนฯ / คำร้อง",for_center_bold_bg)
        worksheet.write('C' + str(inv_row), "วันที่สถานะใบขนฯ\n๐๔๐๙",for_center_bold_bg)
        worksheet.write('D' + str(inv_row), "รหัสวัตถุดิบ / สินค้า", for_center_bold_bg)
        worksheet.write('E' + str(inv_row), "ชนิของ", for_center_bold_bg)
        worksheet.write('F' + str(inv_row), "ปริมาณ", for_center_bold_bg)
        worksheet.write('G' + str(inv_row), "หน่วยนับ", for_center_bold_bg)
        worksheet.write('H' + str(inv_row), "น้ำหนัก", for_center_bold_bg)
        worksheet.write('I' + str(inv_row), "มูลค่า - บัญชี", for_center_bold_bg)
        worksheet.write('J' + str(inv_row), "มูลค่า - ใบขน", for_center_bold_bg)


        count = 1
        for stock in Stocks:
            domain = [('product_id', '=', stock.name)]
            if self.location.complete_name != False:
                domain += [('location_dest_id', '=',self.location.complete_name)]
                # print(domain)
            if self.warehouse.complete_name != False:
                domain += [('location_id', '=',self.warehouse.complete_name)]
                # print(domain)
            if self.date_present != False:
                domain += [('date', '<=',self.date_present)]
                # print(domain)
            # print(domain)
            moves_history = self.env['stock.move.line'].search(domain)
            for move in moves_history:
                # print(move.state)
                if "IN" in move.reference.split("/") and move.state == "done":
                    inv_row += 1
                    domain1 = [('name', '=', move.reference)]
                    stock_picking = self.env['stock.picking'].search(domain1)
                    domain2 = [('reference', '=', move.reference),('product_id', '=', stock.display_name)]
                    valuation = self.env['stock.valuation.layer'].search(domain2)
                    worksheet.write('A' + str(inv_row), count or "", for_center)
                    try:
                        worksheet.write('B' + str(inv_row),stock_picking.petition_number or "", for_center)
                    except:
                        worksheet.write('B' + str(inv_row),"", for_center)
                    worksheet.write('C' + str(inv_row), " ", for_center)
                    if stock_picking.reference_date != False:
                        day, monthth, year = self.day_to_str(stock_picking.reference_date)
                        worksheet.write('C' + str(inv_row), "{}-{}-{}".format(day, monthth, year), for_center)
                    worksheet.write('D' + str(inv_row), stock.default_code or "", for_center)
                    worksheet.write('E' + str(inv_row), stock.name or "", for_center)
                    worksheet.write('F' + str(inv_row), move.qty_done or "", for_center)
                    worksheet.write('G' + str(inv_row), move.product_uom_id.name or "", for_center)
                    worksheet.write('H' + str(inv_row), move.qty_done or "", for_center)
                    worksheet.write('I' + str(inv_row), " ", for_center)
                    # worksheet.write('J' + str(inv_row), '{} x {} = {}'.format(move.qty_done,valuation.unit_cost,(move.qty_done*valuation.unit_cost)), for_center)
                    worksheet.write('J' + str(inv_row), (move.qty_done*valuation.unit_cost) or "", for_center)

                    count += 1

        workbook.close()
        buf = fl.getvalue()
        # vals = {'name': namexls, 'report_file': base64.encodestring(buf)}
        vals = {'name': namexls, 'report_file': base64.encodebytes(buf)}
        self._cr.execute("TRUNCATE return_card_report_excel_export CASCADE")
        wizard_id = self.env['return.card.report.excel.export'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'return.card.report.excel.export',
            'target': 'new',
            'res_id': wizard_id.id,
        }






class return_card_report_excel_export(models.TransientModel):
    _name = 'return.card.report.excel.export'

    report_file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    def action_back(self):
        if self._context is None:
            self._context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'return.card.report',
            'target': 'new',
        }




