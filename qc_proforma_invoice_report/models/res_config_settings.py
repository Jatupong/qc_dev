# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models
from bahttext import bahttext
from num2words import num2words
import locale


class ResCompany(models.Model):
    _inherit = "res.company"

    proforma_invoice_no_form = fields.Char(string='Proforma Invoice No. Form')

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



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    proforma_invoice_no_form = fields.Char(related='company_id.proforma_invoice_no_form', string='Proforma Invoice No. Form', readonly=False)