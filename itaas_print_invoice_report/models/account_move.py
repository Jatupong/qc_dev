# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import fields, api, models, _
from bahttext import bahttext
from num2words import num2words
import locale

class AccountMove(models.Model):
    _inherit = "account.move"

    def baht_text(self, amount):
        amount = round(amount, 2)
        amount_text = str(amount).split('.')
        amount_text_before_point = amount_text[0]
        amount_text_before_ten_point = amount_text_before_point[len(amount_text_before_point) - 2]
        amount_text_before_last_point = amount_text_before_point[len(amount_text_before_point) - 1]
        if int(amount_text_before_ten_point) == 0 and int(amount_text_before_last_point) == 1:
            amount_text_before_point = bahttext(float(amount_text_before_point)).split('เอ็ดบาท')
            amount_text_before_point = amount_text_before_point[0] + 'บาท'
        else:
            amount_text_before_point = bahttext(float(amount_text_before_point))

        amount_text_after_point = '0.' + amount_text[1]
        amount_after_point = float(amount_text_after_point)
        if float(amount_text_after_point) != 0.0:
            if amount_text_after_point[2] == '0':
                amount_text_after_point = 'หนึ่งสตางค์'
            else:
                amount_text_after_point = bahttext(amount_after_point).split('บาท')
                amount_text_after_point = amount_text_after_point[1]
        else:
            amount_text_after_point = 'ถ้วน'

        baht_text = amount_text_before_point.split('ถ้วน')[0] + amount_text_after_point

        return baht_text

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0, len(amount_total_str)):
            if amount_total_str[i] != ".":
                before_point += amount_total_str[i]
            else:
                break

        after_point = float(amount_total) - float(before_point)
        after_point = locale.format("%.2f", float(after_point), grouping=True)
        after_point = float(after_point)
        before_point = float(before_point)

        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4, len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        # n2w_origianl = num2words(float(amount_total))
        n2w_new = ""
        for i in range(len(n2w_origianl)):
            if i == 0:
                n2w_new += n2w_origianl[i].upper()
            else:
                if n2w_origianl[i] != ",":
                    if n2w_origianl[i - 1] == " ":
                        n2w_new += n2w_origianl[i].upper()
                    else:
                        n2w_new += n2w_origianl[i]

        return n2w_new

    def get_line(self, data, max_line):
        # this function will count number of \n
        line_count = data.count("\n")
        if not line_count:
            # print "line 0 - no new line or only one line"
            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                line_count = len(data) / max_line + 1
        elif line_count:
            # print "line not 0 - has new line"
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        if line_count > 1:
            ##############if more then one line, it is new line not new row, so hight will be 80%
            line_count = line_count * 0.8
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        for line in self.invoice_line_ids:
            line_name = self.get_lines(line.name, max_line_lenght)
            # remove by row height to line
            # line_height = row_line_height + ((self.get_line(line.name, max_line_lenght)) * new_line_height)
            line_height = row_line_height * line_name
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print(break_page_line)
        return break_page_line

    def get_break_line_invoice(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        # print 'get_break_line_invoice'
        for line in self.invoice_line_ids:
            # print line.product_id
            # print line.product_id.default_code
            # default_code

            # print count
            line_height = row_line_height + ((self.get_line(line.name, max_line_lenght)) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)
        # print "break_page_line"
        # print break_page_line
        return break_page_line

    def get_reverse_tax_line(self):
        for move in self:
            line_ids = move.line_ids.filtered(lambda r: r.payment_id)
            if line_ids and line_ids[0].payment_id:
                return self.env['account.move.line'].search([('payment_id','=',line_ids[0].payment_id.id),('move_id','!=',move.id)])
            else:
                return False

