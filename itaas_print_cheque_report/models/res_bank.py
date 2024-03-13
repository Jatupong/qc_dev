# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import fields, api, models
from bahttext import bahttext
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class ResBank(models.Model):
    _inherit = "res.bank"

    font_size = fields.Integer('Size', default=22)

    layout_image1_top = fields.Integer('top', default=80)
    layout_image1_left = fields.Integer('left', default=30)
    layout_image1_height = fields.Integer('height', default=60)
    layout_image1_width = fields.Integer('width', default=120)
    layout_image1_image = fields.Binary('image')
    layout_image1_show = fields.Boolean('show', default=True)

    layout_image2_top = fields.Integer('top', default=70)
    layout_image2_right = fields.Integer('right', default=20)
    layout_image2_height = fields.Integer('height', default=60)
    layout_image2_width = fields.Integer('width', default=120)
    layout_image2_image = fields.Binary('image')
    layout_image2_show = fields.Boolean('show', default=True)

    layout_name_top = fields.Integer('Top', default=87)
    layout_name_left = fields.Integer('Left', default=140)
    layout_name_show = fields.Boolean('Show', default=True)

    layout_amount_top = fields.Integer('Top', default=160)
    layout_amount_left = fields.Integer('Left', default=515)
    layout_amount_show = fields.Boolean('Show', default=True)

    layout_baht_top = fields.Integer('Top', default=125)
    layout_baht_left = fields.Integer('Left', default=150)
    layout_baht_show = fields.Boolean('show', default=True)

    layout_date_top = fields.Integer('Top', default=20)
    layout_date_left = fields.Integer('Left', default=600)
    layout_date_spacing = fields.Integer('Spacing', default=5)
    layout_date_show = fields.Boolean('Show', default=True)

    layout_partner_top = fields.Integer('Top', default=87)
    layout_partner_left = fields.Integer('Left', default=140)
    layout_partner_show = fields.Boolean('Show', default=False)

    def get_date_to_bc_year(self, date):
        # print('get_date_to_bc_year ', date)
        new_date = (date + relativedelta(years=543)).strftime('%d-%m-%Y')
        txt = ''.join(str(new_date).split('-'))
        # print('txt ', txt)
        return txt

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
