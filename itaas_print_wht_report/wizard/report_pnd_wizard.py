# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import base64
import xlwt
import math
import math


class report_pnd(models.TransientModel):
    _name = 'pnd.report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    wht_type = fields.Many2one('account.wht.type', string='WHT Type', required=False)
    report_type = fields.Selection([('personal', 'ภงด3'), ('pnd2', 'ภงด2'), ('company', 'ภงด53')], string='Report Type',
                                   required=True)
    month = fields.Char(string='Month')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def default_get(self, fields):
        res = super(report_pnd, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, curr_date.month, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})
        return res

    def print_pnd_report(self):
        print('print_pnd_report ')
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                # 'wht_type': self.wht_type.id,
                'report_type': self.report_type,
                'month': self.month,
                'company_id': self.company_id.id}

        if self.report_type == 'company':
            return self.env.ref('itaas_print_wht_report.action_report_pnd53_id').report_action(self, data=data)
        elif self.report_type == 'personal':
            return self.env.ref('itaas_print_wht_report.action_report_pnd3_id').report_action(self, data=data)
        elif self.report_type == 'pnd2':
            return self.env.ref('itaas_print_wht_report.action_report_pnd2_id').report_action(self, data=data)

    def get_bank_report(self):
        sum_credit = 0
        final_text = ""
        final_text_body = ""

        # move_line_ids = self.env['account.move.line'].search([('date_maturity', '>=', self.date_from),
        #                                                       ('date_maturity', '<=', self.date_to),
        #                                                       ('wht_type', '=', self.wht_type.id)],
        #                                                      order='date_maturity,wht_reference ASC')
        move_line_ids = self.env['account.move.line'].search([('date_maturity', '>=', self.date_from),
                                                              ('date_maturity', '<=', self.date_to),
                                                              ('wht_type.report_type', '=', self.report_type)],
                                                             order='date_maturity,wht_reference ASC')
        move_ids = ""
        inv_row = 1

        if move_line_ids:

            # ลำดับ|เลประจำตัวผู้เสียภาษีอากร|คำนำหน้าชื่อ|ชื่อของผู้มีเงินได้|ชื่อสกุล|ที่อยู่|วันเดือนปี|ประเภทเงินได้|อัตราภาษี|จำนวนเงินที่จ่าย|เงื่อนไขการหักภาษี
            for move in move_line_ids:

                move_ids += str(inv_row) + '|'
                if move.partner_id.vat:
                    move_ids += str(move.partner_id.vat[0:13]) + '|'

                title_name = move.partner_id.title or ''
                name_temp = move.partner_id.name.split(' ')
                if len(name_temp) > 2:
                    title_name = name_temp[0]
                    first_name = name_temp[1]
                    last_name = name_temp[2]
                elif len(name_temp) == 2:
                    first_name = name_temp[0]
                    last_name = name_temp[1]
                else:
                    title_name = " "
                    first_name = name_temp[0]
                    last_name = " "

                if self.report_type == 'company':
                    name = ""
                    for i in name_temp:
                        name += i
                    move_ids+= name + '|'
                elif self.report_type != 'company':
                    move_ids += str(title_name) + '|'

                    move_ids += str(first_name) + '|'
                    move_ids += str(last_name) + '|'

                address = self.get_partner_full_address_text(move.partner_id)
                address_text = ' '.join(address)
                # print("address_text [")
                # for i in address:
                #     print(i)
                # print("]")
                move_ids += address_text + '|'

                if move.date_maturity:
                    date_payment_text = move.date_maturity.strftime('%d/%m/%Y')
                    date_payment_text = date_payment_text.split('/')
                    date = move.date_maturity
                    date_payment = date_payment_text[0] + '/' + date_payment_text[1] + '/' + str(date.year + 543)
                if date_payment:
                    move_ids += date_payment + '|'
                else:
                    move_ids += '|'

                move_ids += str(move.name) + '|'

                wht_tax = int(move.wht_tax.amount)

                if move.amount_before_tax:
                    amount_before_tax = move.amount_before_tax
                else:
                    amount_before_tax = (move.credit + move.debit) * (1 - wht_tax / 100.0)

                move_ids += str(wht_tax) + '|'
                move_ids += str(amount_before_tax) + '|'
                sum_credit+=move.credit
                # move_ids += str(sum_credit) + '|'
                move_ids += str(move.credit) + '|'
                if self.user_has_groups('base.group_no_one'):
                    move_ids +="["
                    for i in move_line_ids:
                        move_ids += " {}:{}".format(i.id,i.credit)
                    move_ids += "] = {}|".format(sum_credit)

                if inv_row != len(move_line_ids):
                    move_ids += '1' + "\r\n"
                else:
                    move_ids += '1'

                final_text = final_text_body + str(move_ids)
                # print('final_text : ',final_text)
                inv_row += 1
        else:
            raise UserError(_('There is record this date range.'))

        values = {
            'name': 'witholding_report.txt',
            # 'datas_fname': 'witholding_report.txt',
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            # 'datas': base64.b64encode(final_text),
            'datas': base64.b64encode((final_text).encode("utf-8")),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

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

    def domain_one_new(self):
        print('ffffff')
        len_pnd1 = total_wht_amount_1 = total_amount_1 = 0
        move_line_ids = self.env['account.move.line'].search([("wht_type.condition", "=", 'pnd2_1')])
        if move_line_ids:
            for line in move_line_ids:
                total_wht_amount_1 += line.credit + line.debit
                print('ggggggg')
                if line.amount_before_tax:
                    total_amount_1 += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount_1 += amount
        else:
            total_amount_1 = 0
            total_wht_amount_1 = 0
        len_pnd1 = len(move_line_ids)
        sum_total = total_amount_1
        sum_total_1 = total_wht_amount_1
        print('len_pnd1', len_pnd1)
        print('sum_total', sum_total)
        print('sum_total_1', sum_total_1)

        return len_pnd1, sum_total, sum_total_1

    def domain_two_new(self):
        print('ffffff')
        len_pnd2 = total_wht_amount_2 = total_amount_2 = 0
        move_line_ids = self.env['account.move.line'].search([("wht_type.condition", "=", 'pnd2_2')])
        if move_line_ids:
            for line in move_line_ids:
                total_wht_amount_2 += line.credit + line.debit
                print('ggggggg')
                if line.amount_before_tax:
                    total_amount_2 += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount_2 += amount
        else:
            total_amount_2 = 0
            total_wht_amount_2 = 0
        len_pnd2 = len(move_line_ids)
        sum_total_2 = total_amount_2
        sum_total_2_2 = total_wht_amount_2

        return len_pnd2, sum_total_2, sum_total_2_2

    def domain_three_new(self):
        print('ffffff')
        len_pnd3 = total_wht_amount_3 = total_amount_3 = 0
        move_line_ids = self.env['account.move.line'].search([("wht_type.condition", "=", 'pnd2_3')])
        if move_line_ids:
            for line in move_line_ids:
                total_wht_amount_3 += line.credit + line.debit
                print('ggggggg')
                if line.amount_before_tax:
                    total_amount_3 += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount_3 += amount
        else:
            total_amount_3 = 0
            total_wht_amount_3 = 0
        len_pnd3 = len(move_line_ids)
        sum_total_3 = total_amount_3
        sum_total_2_3 = total_wht_amount_3

        return len_pnd3, sum_total_3, sum_total_2_3

    def domain_four_new(self):
        print('ffffff')
        len_pnd4 = total_wht_amount_4 = total_amount_4 = 0
        move_line_ids = self.env['account.move.line'].search([("wht_type.condition", "=", 'pnd2_4')])
        if move_line_ids:
            for line in move_line_ids:
                total_wht_amount_4 += line.credit + line.debit
                print('ggggggg')
                if line.amount_before_tax:
                    total_amount_4 += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount_4 += amount
        else:
            total_amount_4 = 0
            total_wht_amount_4 = 0
        len_pnd4 = len(move_line_ids)
        sum_total_4 = total_amount_4
        sum_total_2_4 = total_wht_amount_4

        return len_pnd4, sum_total_4, sum_total_2_4

    def domain_five_new(self):
        print('ffffff')
        len_pnd5 = total_wht_amount_5 = total_amount_5 = 0
        move_line_ids = self.env['account.move.line'].search([("wht_type.condition", "=", 'pnd2_5')])
        if move_line_ids:
            for line in move_line_ids:
                total_wht_amount_5 += line.credit + line.debit
                print('ggggggg')
                if line.amount_before_tax:
                    total_amount_5 += line.amount_before_tax
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount_5 += amount
        else:
            total_amount_5 = 0
            total_wht_amount_5 = 0
        len_pnd5 = len(move_line_ids)
        sum_total_5 = total_amount_5
        sum_total_2_5 = total_wht_amount_5

        return len_pnd5, sum_total_5, sum_total_2_5

    def _get_pnd_info(self, date_from, date_to, type):
        total_amount = total_wht_amount = total_item = total_page = 0

        domain = [('date_maturity', '>=', date_from),
                  ('date_maturity', '<=', date_to),
                  ('wht_type.report_type', '=', type),
                  # ('report_type', '=', report_type),
                  ]
        print('domain : ', domain)
        line_ids = self.env['account.move.line'].search(domain, order='date_maturity, wht_reference ASC')
        print('line_ids : ', line_ids)
        total_item = len(line_ids)

        # print domain
        if line_ids:

            if total_item <= 6:
                total_page = 1
            else:
                page = len(line_ids) / 6
                test = len(line_ids) % 6
                if test != 0:
                    page += 1
                print('TEST:::', page)
                print('TEST:::', test)
                total_page = int(round(page, 0))

            for line in line_ids:
                total_wht_amount += line.credit + line.debit
                # print('fffffff', total_wht_amount)
                if line.amount_before_tax:

                    total_amount += line.amount_before_tax
                    # print('jjjjjjjjj',total_amount)
                else:
                    wht_tax = line.wht_tax.amount
                    amount = (line.credit + line.debit) * (1 - wht_tax / 100.0)
                    total_amount += amount
        else:
            total_amount = 0
            total_wht_amount = 0
            total_page = 0

        # print('total_item', total_item)
        # print('len(line_ids)', len(line_ids))
        # print('total_page', total_page)
        #
        len_pnd1, sum_total, sum_total_1 = self.domain_one_new()
        len_pnd2, sum_total_2, sum_total_2_2 = self.domain_two_new()
        len_pnd3, sum_total_3, sum_total_2_3 = self.domain_three_new()
        len_pnd4, sum_total_4, sum_total_2_4 = self.domain_four_new()
        len_pnd5, sum_total_5, sum_total_2_5 = self.domain_five_new()

        return {
            'total_amount': total_amount,
            'total_wht_amount': total_wht_amount,
            'total_item': total_item,
            'total_page': total_page,

            'len_pnd1': len_pnd1,
            'total_amount_pnd1': sum_total,
            'total_wht_amount1': sum_total_1,

            'len_pnd2': len_pnd2,
            'total_amount_pnd2': sum_total_2,
            'total_wht_amount2': sum_total_2_2,

            'len_pnd3': len_pnd3,
            'total_amount_pnd3': sum_total_3,
            'total_wht_amount3': sum_total_2_3,

            'len_pnd4': len_pnd4,
            'total_amount_pnd4': sum_total_4,
            'total_wht_amount4': sum_total_2_4,

            'len_pnd5': len_pnd5,
            'total_amount_pnd5': sum_total_5,
            'total_wht_amount5': sum_total_2_5,

        }


class report_report_pnd3(models.AbstractModel):
    _name = 'report.itaas_print_wht_report.report_pnd3_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('ddddd')

        if not data:
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        doc_model = 'pnd.report'

        pnd_info = docs._get_pnd_info(data['date_from'], data['date_to'], data['report_type'])
        print('ddddd', type)
        docargs = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'data': data,
            'docs': docs,
            'pnd_info': pnd_info,
            'company_id': docs.company_id,
        }

        return docargs


class report_report_pnd53(models.AbstractModel):
    _name = 'report.itaas_print_wht_report.report_pnd53_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        doc_model = 'pnd.report'

        pnd_info = docs._get_pnd_info(data['date_from'], data['date_to'], data['report_type'])
        docargs = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'data': data,
            'docs': docs,
            'pnd_info': pnd_info,
            'company_id': docs.company_id,
        }

        return docargs


class report_report_pnd2(models.AbstractModel):
    _name = 'report.itaas_print_wht_report.report_pnd2_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        doc_model = 'pnd.report'

        pnd_info = docs._get_pnd_info(data['date_from'], data['date_to'], data['report_type'])
        print('kkkkk', data['report_type'])

        docargs = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'data': data,
            'docs': docs,
            'pnd_info': pnd_info,
            'company_id': docs.company_id,
        }

        return docargs


class AccountMoveLine(models.AbstractModel):
    _inherit = 'account.move.line'

    def get_num_page(self, record, max_record):
        return int(math.ceil((record / max_record)))