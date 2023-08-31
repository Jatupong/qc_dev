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

class pnd53_report(models.TransientModel):
    _name = 'pnd53.report'
    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)
    report_type = fields.Selection([('personal', 'ภงด3'), ('company', 'ภงด53')],string='Report Type', required=True)
    month = fields.Char(string='Month')
    company_id = fields.Many2one('res.company')

    @api.model
    def default_get(self, fields):
        res = super(pnd53_report, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, curr_date.month, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})
        return res

    def print_pnd53_report(self):
        print('bbbbbbbbbbb')
        # data = {}
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type,
                'month': self.month, 'company_id': self.company_id}
        # data['form'] = self.read(['date_from', 'date_to', 'report_type', 'month','company_id'])[0]

        if data['report_type'] == 'company':
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd53_id', data=data)
            return self.env.ref('itaas_print_wht_report.action_report_pnd53_id').report_action(self, data=data)
        elif data['report_type'] == 'personal':
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd3_id', data=data)
            return self.env.ref('itaas_print_wht_report.action_report_pnd3_id').report_action(self, data=data)
        else:
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd2_id', data=data)
            return self.env.ref('itaas_print_wht_report.action_report_pnd2_id').report_action(self, data=data)

    def print_pnd53_report_to_text(self):
        print('print_pnd53_report_to_text__WHT')
        context = dict(self._context or {})
        file_type = context.get('file')

        fl = StringIO()
        workbook = xlwt.Workbook(encoding='utf-8')

        font = xlwt.Font()
        font.bold = True
        font.bold = True
        for_right = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right.num_format_str = '#,###.00'
        for_right_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right_bold.num_format_str = '#,###.00'
        for_center = xlwt.easyxf(
            "font: name  Times New Roman, color black,  height 180; align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz left,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_center_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left_bold_no_border = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz left,vertical center;")

        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name  Times New Roman, height 300,color black;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top thin, bottom thin, left thin, right thin;'
            'pattern:  pattern_fore_colour white, pattern_back_colour white'
        )

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '#,###.00'
        # cr, uid, context = self.env.args
        final_text = ""
        final_text_body = ""

        # -------------------------------------- PND 3 ----------------------------------------
        if self.report_type == 'personal':
            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_type.name', '=', 'personal'), ('wht_tax', '!=', False), ('account_id.wht', '=', True),
                 ('ignore_wht', '=', False)],
                order='date_maturity ASC')
            # move_line_ids = self.env['account.move.line'].browse([232863])
            print('move_line_ids:',move_line_ids)
            print('move_line_ids:',len(move_line_ids))
            move_ids = ""
            inv_row = 1
            title_name = ""
            for move in move_line_ids:
                move_ids += str(inv_row) + '|'
                if move.tax_onetime:
                    move_ids += str(move.tax_onetime) + '|'
                else:
                    if move.move_id.partner_id.is_onetime:
                        move_ids += str(move.move_id.tax_onetime) + '|'
                    else:
                        move_ids += str(move.move_id.partner_id.vat) + '|'
                if move.partner_id:
                    move_ids += str(move.partner_id.branch_no or '') + '|'
                elif move.move_id.partner_id:
                    move_ids += str(move.move_id.partner_id.branch_no or '') + '|'

                print('move========= START:',move)
                if move.name_onetime:
                    print('1.1')
                    name_temp = move.name_onetime.split(' ')
                    if len(name_temp) >= 3:
                        print('1.2.1')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = name_temp[2]
                    elif len(name_temp) == 2:
                        print('1.2.2')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = " "
                    else:
                        print('1.2.3')
                        title_name = ""
                        first_name = name_temp[0]
                        last_name = " "
                    # first_name = name_temp[0]
                    # last_name = " ".join(name_temp[1:])
                elif move.move_id.partner_id.is_onetime:
                    print('1.2')
                    name_temp = move.move_id.name_onetime.split(' ')
                    if len(name_temp) >= 3:
                        print('1.2.1')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = name_temp[2]
                    elif len(name_temp) == 2:
                        print('1.2.2')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = " "
                    else:
                        print('1.2.3')
                        title_name = ""
                        first_name = name_temp[0]
                        last_name = " "

                    # title_name = ""
                    # first_name = name_temp[0]
                    # last_name = " ".join(name_temp[1:])
                elif move.move_id.partner_id.title:
                    print('1.3')
                    title_name = move.move_id.partner_id.title.name
                    name_temp = move.move_id.partner_id.name.split(' ')
                    first_name = name_temp[0]
                    last_name = " ".join(name_temp[1:])
                    # last_name = name_temp[1:]
                else:
                    print('1.4')
                    name_temp = move.move_id.partner_id.name.split(' ')
                    print('name_temp:',name_temp)
                    if len(name_temp) >= 3:
                        print('2.1')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = name_temp[2]
                    elif len(name_temp) == 2:
                        print('2.2')
                        title_name = name_temp[0]
                        first_name = name_temp[1]
                        last_name = " "
                    else:
                        print('2.3')
                        title_name = ""
                        first_name = name_temp[0]
                        last_name = " "

                # if title_name:
                #     move_ids += str(title_name) + '|'
                # else:
                #     move_ids += '|'

                print('title_name__:',title_name)
                print('first_name__:',first_name)
                print('last_name__:',last_name)

                move_ids += str(title_name) + '|'
                move_ids += str(first_name) + '|'
                move_ids += str(last_name) + '|'


                if move.address_onetime:
                    move_ids += str(move.address_onetime) + '|'
                else:
                    if move.move_id.partner_id.is_onetime:
                        move_ids += str(move.move_id.address_onetime) + '|'
                    else:
                        # address = self.get_partner_full_address_text(move.move_id.partner_id)
                        # print('address:', address)
                        # address_text = ' '.join(address)
                        # move_ids += address_text + '|'
                        move_ids += str(move.partner_id.street or '') + '|'
                        move_ids += str(move.partner_id.street2 or '') + '|'
                        move_ids += str(move.partner_id.sub_district_id.name or '') + '|'
                        move_ids += str(move.partner_id.district_id.name or '') + '|'
                        move_ids += str(move.partner_id.state_id.name or '') + '|'
                        move_ids += str(move.partner_id.zip or '') + '|'

                # if move.partner_id.street:
                #     move_ids += str(move.partner_id.street)[0:30]
                #     move_ids += str(move.partner_id.street2)[0:30]
                #     move_ids += str(move.partner_id.city)[0:30]
                #     move_ids += str(move.partner_id.state_id.name)[0:40]
                #     move_ids += str(move.partner_id.zip)[0:5] + '|'
                # else:
                #     move_ids += '|'
                # else:
                #     move_ids += '|'
                # if move.partner_id.street2:
                #     move_ids += str(move.partner_id.street2)[0:30]
                # else:
                #     move_ids += '|'
                # if move.partner_id.city:
                #     move_ids += str(move.partner_id.city)[0:30]
                # else:
                #     move_ids += '|'
                # if move.partner_id.state_id and move.partner_id.state_id.name:
                #     move_ids += str(move.partner_id.state_id.name)[0:40]
                # else:
                #     move_ids += '|'
                # if move.partner_id.zip:
                #     move_ids += str(move.partner_id.zip)[0:5] + '|'
                # else:
                #     move_ids += '|'

                if move.date_maturity:
                    # date = datetime.strptime(move.date_maturity, "%Y-%m-%d").date()
                    date = move.date_maturity
                    if len(str(date.day)) < 2:
                        day = '0' + str(date.day)
                    else:
                        day = str(date.day)
                    if len(str(date.month)) < 2:
                        month = '0' + str(date.month)
                    else:
                        month = str(date.month)
                    date_payment = day + '/' + month + '/' + str(date.year + 543)
                if date_payment:
                    move_ids += date_payment + '|'
                else:
                    move_ids += '|'
                # move_ids += strToDate(move.date_maturity).strftime("%d/%m/%Y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    wht_type = str(move.wht_tax.amount)[0]
                    # if str(move.wht_tax.amount) == '1%':
                    #     wht_type = '1'
                    # elif move.wht_type == '2%':
                    #     wht_type = '2'
                    # elif move.wht_type == '3%':
                    #     wht_type = '3'
                    # elif move.wht_type == '5%':
                    #     wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'

                if inv_row != len(move_line_ids):
                    move_ids += '1' + "\r\n"
                else:
                    move_ids += '1'

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)

                inv_row += 1

        # -------------------------------------- PND 53 ----------------------------------------
        elif self.report_type == 'company':
            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_type.name', '=', 'company'), ('wht_tax', '!=', False), ('account_id.wht', '=', True),
                 ('ignore_wht', '=', False)],
                order='date_maturity,wht_reference ASC')
            move_ids = ""
            inv_row = 1

            for move in move_line_ids:
                title_name =''
                first_name =''
                last_name =''
                move_ids += str(inv_row) + '|'
                if move.tax_onetime:
                    move_ids += str(move.tax_onetime) + '|'
                else:
                    if move.move_id.partner_id.is_onetime:
                        move_ids += str(move.move_id.tax_onetime) + '|'
                    else:
                        move_ids += str(move.move_id.partner_id.vat) + '|'

                move_ids += str(move.move_id.partner_id.branch_no) + '|'
                if move.name_onetime:
                    name_temp = move.name_onetime.split(' ')
                    first_name = name_temp[0]
                    last_name = " ".join(name_temp[1:])
                elif move.move_id.partner_id.is_onetime:
                    name_temp = move.move_id.name_onetime.split(' ')

                    first_name = name_temp[0]
                    last_name = " ".join(name_temp[1:])
                else:
                    name_temp = move.partner_id.name.split(' ')
                    first_name = name_temp[0]
                    last_name = " ".join(name_temp[1:])

                move_ids += str(first_name) + '|'
                move_ids += str(last_name) + '|'


                if move.address_onetime:
                    move_ids += str(move.address_onetime) + '|'
                else:
                    if move.move_id.partner_id.is_onetime:
                        move_ids += str(move.move_id.address_onetime) + '|'
                    else:
                        # address = self.get_partner_full_address_text(move.move_id.partner_id)
                        # print('address:', address)
                        # address_text = ' '.join(address)
                        # move_ids += address_text + '|'
                        move_ids += str(move.partner_id.street or '') + '|'
                        move_ids += str(move.partner_id.street2 or '') + '|'
                        move_ids += str(move.partner_id.sub_district_id.name or '') + '|'
                        move_ids += str(move.partner_id.district_id.name or '') + '|'
                        move_ids += str(move.partner_id.state_id.name or '') + '|'
                        move_ids += str(move.partner_id.zip or '') + '|'




                if move.date_maturity:
                    # date = datetime.strptime(move.date_maturity, "%Y-%m-%d").date()
                    date = move.date_maturity
                    if len(str(date.day)) < 2:
                        day = '0' + str(date.day)
                    else:
                        day = str(date.day)
                    if len(str(date.month)) < 2:
                        month = '0' + str(date.month)
                    else:
                        month = str(date.month)
                    date_payment = day + '/' + month + '/' + str(date.year + 543)
                if date_payment:
                    move_ids += date_payment + '|'
                else:
                    move_ids += '|'
                # move_ids += strToDate(move.date_maturity).strftime("%d/%m/%Y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    wht_type = str(move.wht_tax.amount)[0]
                    # if move.wht_type == '1%':
                    #     wht_type = '1'
                    # elif move.wht_type == '2%':
                    #     wht_type = '2'
                    # elif move.wht_type == '3%':
                    #     wht_type = '3'
                    # elif move.wht_type == '5%':
                    #     wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'

                if inv_row != len(move_line_ids):
                    move_ids += '1' + "\r\n"
                else:
                    move_ids += '1'

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)
                print('final_text:', final_text)
                inv_row += 1

        # ------------------------------------ End PND 53 -------------------------------------------------

        else:
            raise UserError(_('There is record this date range.'))
        if not final_text:
            raise UserError(_('There is record this date range.'))

        values = {
            'name': "Witholding Report.txt",
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode((final_text).encode("utf-8")),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # '/web/content/' + attachment.id + '?download=true'

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def get_partner_full_address_text(self, partner_id):
        address = []
        if partner_id.country_id.code == 'TH':
            if partner_id.street:
                address.append(str(partner_id.street))
            if partner_id.street2:
                address.append(str(partner_id.street2))

            if partner_id.state_id and partner_id.state_id.code == 'BKK':
                if partner_id.sub_district_id:
                    address.append('แขวง' + str(partner_id.sub_district_id.name))
                if partner_id.district_id:
                    address.append('เขต' + str(partner_id.district_id.name))
                elif partner_id.city:
                    address.append('เขต' + str(partner_id.city))

                if partner_id.state_id:
                    address.append(str(partner_id.state_id.name))
            else:
                if partner_id.sub_district_id:
                    address.append('ต.' + str(partner_id.sub_district_id.name))

                if partner_id.district_id:
                    address.append('อ.' + str(partner_id.district_id.name))
                elif partner_id.city:
                    address.append('อ.' + str(partner_id.city))

                if partner_id.state_id:
                    address.append('จ.' + str(partner_id.state_id.name))
        else:

            if partner_id.street:
                address.append(str(partner_id.street))
            if partner_id.street2:
                address.append(str(partner_id.street2))
            if partner_id.city:
                address.append(str(partner_id.city))
            if partner_id.state_id:
                address.append(str(partner_id.state_id.name))

        if partner_id.zip:
            address.append(str(partner_id.zip))
        # print('get_partner_full_address_text address : ',address)
        return address

    def _get_pnd_info(self, date_from, date_to, type):
        total_amount = total_wht_amount = total_item = total_page = 0

        domain = [('date_maturity', '>=', date_from),
                  ('date_maturity', '<=', date_to),
                  ('wht_type', '=', type)
                  ]
        print('domain : ',domain)
        line_ids = self.env['account.move.line'].search(domain, order='date_maturity, wht_reference ASC')
        print('line_ids : ',line_ids)
        total_item = len(line_ids)

        # print domain
        if line_ids:
            if total_item <= 10:
                total_page = 1
            else:
                total_page = len(line_ids) * 10 + 10 / 10

            for line in line_ids:
                total_wht_amount += line.credit + line.debit
                if line.amount_before_tax:
                    total_amount += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount += amount
        else:
            total_amount = 0
            total_wht_amount = 0
            total_page = 0

        return {
            'total_amount': total_amount,
            'total_wht_amount': total_wht_amount,
            'total_item': total_item,
            'total_page':total_page,
        }
