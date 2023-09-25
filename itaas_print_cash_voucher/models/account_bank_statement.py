# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext
from openerp.exceptions import UserError
from datetime import datetime, date
# from num2words import num2words
import locale


class Account_Bank_Statement_line(models.Model):
    _inherit ="account.bank.statement.line"

    demartment_id = fields.Many2one('hr.department', string="Department")





class Account_Bank_Statement(models.Model):
    _inherit ="account.bank.statement"

    number = fields.Char(string="number")

    @api.model
    def create(self, vals):
        request = super(Account_Bank_Statement, self).create(vals)
        request.write({'number': self.env['ir.sequence'].next_by_code('Cash.register'), })

        return request



    def baht_text(self, amount_total):
        return bahttext(amount_total)

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

        # print before_point
        # print after_point
        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4, len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        # print n2w_origianl
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

        # print n2w_origianl
        # print n2w_new
        return n2w_new



    def get_lines(self, data, max_line):
        # this function will count number of \n
        # print  data
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
        print("final line")
        print(line_count)
        return line_count



    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        print('get_break_line')
        break_page_line = []
        count_height = 0
        count = 1

        for line in self.line_ids:

            # count += 1
            print(count)
            print(line.name)

            line_name = self.get_lines(line.name, max_line_lenght)
            line_height = row_line_height + ((line_name) * new_line_height)
            count_height += line_height
            if count_height > max_body_height:
                print('count')
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        return break_page_line







