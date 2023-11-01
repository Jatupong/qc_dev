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

    def day_to_str(self,date_from):
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
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 10)
            worksheet.set_column('H:H', 8)
            worksheet.set_column('I:I', 13)


            worksheet.set_column('J:J', 15)
            worksheet.set_column('K:K', 15)
            worksheet.set_column('L:L', 15)
            worksheet.set_column('M:M', 15)
            worksheet.set_column('N:N', 15)
            worksheet.set_column('O:O', 15)
            worksheet.set_column('P:P', 15)
            worksheet.set_column('Q:Q', 15)
            worksheet.set_column('R:R', 15)


            # domain = [('product_id', '=', self.product.name)]

            # if self.category_id.complete_name != False:
            #     domain += [('categ_id', '=', self.category_id.complete_name)]
            #     # print(domain)
            # if self.product.name != False:
            #     domain += [('name', '=', self.product.name)]
            #     print(domain)

            domain = [('state', '=', 'done'),
                      ('date', '>=', self.date_from),
                      ('date', '<=', self.date_to),

                      # ('company_id', '=', self..company.name),

                      # ('move_line_ids.location_id', 'in', self.location.name),

                      # '|', ('location_dest_id', 'in', location_ids.ids), ('location_id', 'in', location_ids.ids),

                      ('product_id', 'in', self.product.name),
                      # ('is_inventory', '=', False),
                      # ('picking_type_id.code', 'in', ['internal']),
                      ]


            Stocks = self.env['stock.picking'].search(domain)
            print(Stocks)

            inv_row = 1
            worksheet.merge_range('A' + str(inv_row) + ':I' + str(inv_row), 'รายงานการซื้อสินค้า', for_center_bold)


            inv_row += 1
            day, monthth, year = self.day_to_str(date.today())
            worksheet.merge_range('A' + str(inv_row) + ':I' + str(inv_row),"ข้อมูลวันที่ {} - {}".format(self.date_from,self.date_to), for_center_bold)

            inv_row += 2
            worksheet.write('D' + str(inv_row), "คลังสินค้า", for_center_bold)
            worksheet.write('E' + str(inv_row), self.location.name, for_center_bold)
            inv_row += 1
            worksheet.write('D' + str(inv_row), "Catergory", for_center_bold)
            worksheet.write('E' + str(inv_row), self.category_id.name, for_center_bold)
            inv_row += 1
            worksheet.write('D' + str(inv_row), "สินค้า", for_center_bold)
            worksheet.write('E' + str(inv_row), self.product.name, for_center_bold)

            inv_row += 2
            worksheet.merge_range('A' + str(inv_row) + ':G' + str(inv_row)," ", for_center_bold)
            worksheet.merge_range('H' + str(inv_row) + ':I' + str(inv_row), "ยอด", for_center_bold)

            inv_row += 1
            worksheet.set_row(inv_row - 1, 40)
            worksheet.write('A' + str(inv_row), "Suppiler", for_center_bold)
            worksheet.write('B' + str(inv_row), "วันที่เข้ารับ", for_center_bold)
            worksheet.write('C' + str(inv_row), "Picking Number", for_center_bold)
            worksheet.write('D' + str(inv_row), "วันที่ตาม PO", for_center_bold)
            worksheet.write('E' + str(inv_row), "เลขที่อ้างอิง", for_center_bold)
            worksheet.write('F' + str(inv_row), "Bills", for_center_bold)
            worksheet.write('G' + str(inv_row), "Lot", for_center_bold)
            worksheet.write('H' + str(inv_row), "จำนวน", for_center_bold)
            worksheet.write('I' + str(inv_row), "มูลค่า", for_center_bold)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

            # count = 1
            # for stock in Stocks:
            #     domain = [('product_id', '=', self.product.name), ('reference', '=', stock.name)]
            #     # if self.location.complete_name != False:
            #     #     domain = [('product_id', '=', self.product.name), ('reference', '=', stock.name)]
            #     #     print(domain)
            #     # if self.warehouse.complete_name != False:
            #     #     domain = [('product_id', '=', self.product.name), ('reference', '=', stock.name)]
            #     #     print(domain)
            #     # if self.date_present != False:
            #     #     domain += [('date', '<=', self.date_present)]
            #     #     print(domain)
            #     print(domain)
            #     worksheet.write('C' + str(inv_row), stock.name, for_center)
            #     moves_history = self.env['stock.move.line'].search(domain)
            #     for move in moves_history:
            #         # print(move.state)
            #         if "IN" in move.reference.split("/") and move.state == "done":
            #             inv_row += 1
            #             domain1 = [('name', '=', move.reference)]
            #             stock_picking = self.env['stock.picking'].search(domain1)
            #             domain2 = [('reference', '=', move.reference), ('product_id', '=', stock.display_name)]
            #             valuation = self.env['stock.valuation.layer'].search(domain2)
            #             worksheet.write('A' + str(inv_row), stock.partner_id.name or '', for_center_border)
            #             try:
            #                 worksheet.write('B' + str(inv_row), stock_picking.petition_number or "", for_center)
            #             except:
            #                 worksheet.write('B' + str(inv_row), "", for_center)
            #             worksheet.write('C' + str(inv_row), stock.location_id or "", for_center)
            #             if stock_picking.reference_date != False:
            #                 day, monthth, year = self.day_to_str(stock_picking.reference_date)
            #             # worksheet.write('C' + str(inv_row), "{}-{}-{}".format(day, monthth, year), for_center)
            #             # worksheet.write('C' + str(inv_row), stock.location_id, for_center)
            #             worksheet.write('D' + str(inv_row), stock.default_code or "", for_center)
            #             worksheet.write('E' + str(inv_row), stock.name or "", for_center)
            #             worksheet.write('F' + str(inv_row), move.qty_done or "", for_center)
            #             worksheet.write('G' + str(inv_row), move.product_uom_id.name or "", for_center)
            #             worksheet.write('H' + str(inv_row), move.qty_done or "", for_center)
            #             worksheet.write('I' + str(inv_row), " ", for_center)
            #             worksheet.write('J' + str(inv_row), (move.qty_done * valuation.unit_cost) or "", for_center)
            #
            #             count += 1
            #
            # workbook.close()
            # buf = fl.getvalue()
            # vals = {'name': namexls, 'report_file': base64.encodestring(buf)}
            # self._cr.execute("TRUNCATE product_purchase_report_excel_export CASCADE")
            # wizard_id = self.env['product.purchase.report.excel.export'].create(vals)
            # return {
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'product.purchase.report.excel.export',
            #     'target': 'new',
            #     'res_id': wizard_id.id,
            # }


# ---------------------------------------------------------------------------------------------------------------------------------------------------------

            inv_row = 9
            for stock in Stocks:
                # domain = [('product_id', '=', stock.name)]
                # moves_history = self.env['stock.move.line'].search(domain)
                #     for move in moves_history:
                worksheet.write(inv_row, 0, stock.partner_id.name or ' ', for_center_border)
                worksheet.write(inv_row, 1, stock.scheduled_date or ' ', for_center_border_date)
                worksheet.write(inv_row, 2, stock.name or ' ', for_center_border)
                worksheet.write(inv_row, 3, stock.date_done or ' ', for_center_border_date)
                worksheet.write(inv_row, 4, stock.group_id.name or ' ', for_center_border)

                # account.move
                domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                ]
                move_bill = self.env['account.move'].search(domain)
                for b in move_bill:
                    worksheet.write(inv_row, 5, b.name or ' ', for_center_border)

                domain = [('state', '=', 'done'),
                          ('date', '>=', self.date_from),
                          ('date', '<=', self.date_to),
                          ('product_id', '=', self.product.name),
                          ('reference','=',stock.name),
                          ]
                moves_history = self.env['stock.move.line'].search(domain)
                for i in moves_history.lot_id:
                    worksheet.write(inv_row, 6, i.name or ' ', for_center_border)

                domain = [
                          ('product_id', '=', self.product.name),
                          ('reference','=',stock.name),
                          ]
                moves_layer = self.env['stock.valuation.layer'].search(domain)
                for o in moves_layer:
                        # qty = 0
                        # for Zum in o.valuation.layer:
                        #     qty += Zum.o.quantity
                        #
                        # value = 0
                        # for Zum in o.valuation.layer:
                        #     value += Zum.o.value

                    worksheet.write(inv_row, 7, abs(o.quantity) or '0', for_center_border)

                # worksheet.write(inv_row, 7, stock.show_validate or '', for_center_border)
                worksheet.write(inv_row, 8, abs(o.value) or '0', for_center_border)

            inv_row += 1



            moves_layer = self.env['stock.valuation.layer'].search(domain)
            qty = 0
            value = 0

            for o in moves_layer:
                qty += abs(o.quantity)
                value += abs(o.value)


                # total_cost_qty = sum(stock.get_cost_qty() for stock in Stocks)
            # total_cost_value = sum(stock.get_cost_value() for stock in Stocks)


            # worksheet.merge_range('A' + str(inv_row) + ':G' + str(inv_row), " ", for_right_bold_bg)
            worksheet.write(inv_row, 0, '', for_right_bold_bg)
            worksheet.write(inv_row, 1, '', for_right_bold_bg_no_border_left_right)
            worksheet.write(inv_row, 2, '', for_right_bold_bg_no_border_left_right)
            worksheet.write(inv_row, 3, '', for_right_bold_bg_no_border_left_right)
            worksheet.write(inv_row, 4, '', for_right_bold_bg_no_border_left_right)
            worksheet.write(inv_row, 5, '', for_right_bold_bg_no_border_left_right)
            worksheet.write(inv_row, 6, 'รวม', for_right_bold_bg_no_border_right)
            worksheet.write(inv_row, 7, qty, for_right_bold_bg)
            worksheet.write(inv_row, 8, value, for_right_bold_bg)




                # worksheet.merge_range('A' + str(inv_row) + ':G' + str(inv_row), "รวม", for_right_bold)

            workbook.close()
            buf = fl.getvalue()
            vals = {'name': namexls, 'report_file': base64.encodestring(buf)}
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

