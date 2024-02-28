# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from num2words import num2words
import locale


class stock_move_line(models.Model):
    _inherit = "stock.move.line"

    def get_field_json(self, field):
        ans = []
        for i in field.fields_get():
            my_code = "field.{}".format(i)
            value = eval(my_code)
            print("field : {} var = {}".format(i, value))
            if str(i) == 'display_name':
                ans.append("{}".format(value))

        return ans



class StockPicking(models.Model):
    _inherit = "stock.picking"

    buyer_confirm = fields.Many2one('res.users', string="Buyer Confirm")

    def sale_order(self, data, field):
        domain = [('name', '=', data)]
        order = self.env['sale.order'].search(domain)
        if len(order) == 1:
            my_code = "order.{}".format(field)
            value = eval(my_code)
            print("Have field[{}]".format(value))
            if "line" in str(field):
                my_code = "order.{}.filtered(lambda x:x.display_type not in ['line_note','line_section'])".format(field)
                value = eval(my_code)
            return value
        else:
            return ""

    def get_lines(self, data, max_line):
        line_count = 0
        if data:
            # this function will count number of \n
            line_count = data.count("\n")
            if not line_count:
                #  print "line 0 - no new line or only one line"
                # lenght the same with line max
                if not len(data) % max_line:
                    line_count = len(data) / max_line
                # lenght not the same with line max
                # if less than line max then will be 0 + 1
                # if more than one, example 2 line then will be 1 + 1
                else:
                    line_count = len(data) / max_line + 1
            elif line_count:
                # print ("line not 0 - has new line", line_count)
                # if have line count mean has \n then will be add 1 due to the last row have not been count \n
                line_count += 1
                data_line_s = data.split('\n')
                for x in range(0, len(data_line_s), 1):
                    if len(data_line_s[x]) > max_line:
                        # print ("more than one line")
                        line_count += len(data_line_s[x]) / max_line

        return line_count

    def get_break_line_delivery(self, order_line, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        for line in order_line:

            line_default_code = self.get_lines(line.product_id.code or '', 15)
            line_name = self.get_lines(line.product_id.name, max_line_lenght)
            line_lot_name = self.get_lines(line.lot_name or '', max_line_lenght)
            line_lot_id = self.get_lines(line.lot_id.name, max_line_lenght)
            get_line = max(line_default_code, line_name, line_lot_name, line_lot_id)

            line_height = row_line_height + ((get_line) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1

        # last page
        break_page_line.append(count - 1)

        return break_page_line

    def get_break_line_06(self, order_line, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        for line in order_line:

            line_default_code = self.get_lines(line.product_id.code or '', 15)
            line_name = self.get_lines(line.product_id.name, max_line_lenght)
            line_lot_name = self.get_lines(line.lot_name or '', max_line_lenght)
            line_lot_id = self.get_lines(line.lot_id.name, max_line_lenght)
            get_line = max(line_default_code, line_name, line_lot_name, line_lot_id)

            line_height = row_line_height + ((get_line) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1

        # last page
        break_page_line.append(count - 1)

        return break_page_line

    def get_break_line_01(self, order_line, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        for line in order_line:

            line_default_code = self.get_lines(line.product_id.code or '', 15)
            line_name = self.get_lines(line.product_id.name, max_line_lenght)
            line_lot_name = self.get_lines(line.lot_name or '', max_line_lenght)
            line_lot_id = self.get_lines(line.lot_id.name, max_line_lenght)
            get_line = max(line_default_code, line_name, line_lot_name, line_lot_id)

            line_height = row_line_height + ((get_line) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1

        # last page
        break_page_line.append(count - 1)

        return break_page_line

    def unique_grade_report(self):
        grades_displayed = set()
        unique_grades = []
        move_lines = self.mapped('move_line_ids')
        for move_line in move_lines:
            product = move_line.product_id

            if product and product.product_ceg_th:
                product_ceg_th = product.product_ceg_th
                if product_ceg_th not in grades_displayed:
                    grades_displayed.add(product_ceg_th)
                    unique_grades.append(product_ceg_th)
        return unique_grades


    # @api.multi
    # def get_report_values(self, docids, data):
    #     print('get_report_values =====1')
    #     print(docids)
    #     result = []
    #     line = []
    #
    #     porduct_id = self.env['stock.move.line'].browse(docids)
    #     print('porduct_id', porduct_id)
    #
    #     result.append(line)
    #     print('lineline', line)
    #     return {
    #         'doc_ids': docids,
    #         'data': data,
    #         'docs': porduct_id,
    #         'result': result
    #
    #     }
