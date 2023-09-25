# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from odoo import api,fields, models
from odoo.osv import osv
# from odoo.report import report_sxw
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import math

class report_report_pnd3(models.AbstractModel):
    _name = 'report.itaas_print_wht_report.report_pnd3_id'

    def _get_header_info(self, date_from, date_to, company_id):
        print('44444444')
        print('vbbbbbbbbbbbbbbbbbbbbbbbbbbb')
        return {
            'date_from': datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).strftime('%Y-%m-%d'),
            'date_to': datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).strftime('%Y-%m-%d'),
            'company_vat': company_id.vat,
            'company_branch': company_id.branch_no,
            'company_name': company_id.name,
            'company_building': company_id.building,
            'company_roomnumber': company_id.roomnumber,
            'company_floornumber': company_id.floornumber,
            'company_village': company_id.village,
            'company_house_number': company_id.house_number,
            'company_moo_number': company_id.moo_number,
            'company_soi_number': company_id.soi_number,
            'company_street': company_id.street,
            'company_tumbon': company_id.street2,
            'company_city' : company_id.city,
            'company_province': company_id.state_id.name,
            'company_code': company_id.zip,
            'company_phone': company_id.phone
        }

    def _get_tax_month(self, date_from, date_to, company_id,type):
        print('5555555')
        print('PND3333333')
        total_amount = 0
        total_wht_amount = 0
        total_item = 0
        total_page = 0
        # wht tax calculation
        domain = [('wht_type.name','=',type),('wht_tax','!=',False),('ignore_wht', '=',False)]
        domain.append(('date_maturity', '>=', date_from))
        domain.append(('date_maturity', '<=', date_to))
        domain.append(('company_id', '=', company_id.id))
        line_ids = self.env['account.move.line'].search(domain)
        print('line_ids:',line_ids)
        print('type:',type)
        print('company_id:',company_id)
        # print domain
        if line_ids:
            for line in line_ids:
                amt_percent = 0
                print("line_ids:",line_ids)
                print("wht_tax:", line.wht_tax.type_name)
                # if line.wht_tax.type_name == 0:
                #     amt_percent = 1
                # elif line.wht_tax.type_name == '1':
                #     amt_percent = 1.5
                # elif line.wht_tax.type_name == '2':
                #     amt_percent = 2
                # elif line.wht_tax.type_name == '3':
                #     amt_percent = 3
                # elif line.wht_tax.type_name == '4':
                #     amt_percent = 5
                # elif line.wht_tax.type_name == '5':
                #     amt_percent = 1
                # elif line.wht_tax.type_name == '6':
                #     amt_percent = 1.5
                # elif line.wht_tax.type_name == '7':
                #     amt_percent = 2
                # elif line.wht_tax.type_name == '8':
                #     amt_percent = 3
                # elif line.wht_tax.type_name == '9':
                #     amt_percent = 5
                # elif line.wht_tax.type_name == '10':
                #     amt_percent = 1
                # elif line.wht_tax.type_name == '11':
                #     amt_percent = 1.5
                # elif line.wht_tax.type_name == '12':
                #     amt_percent = 2
                # elif line.wht_tax.type_name == '13':
                #     amt_percent = 3
                # elif line.wht_tax.type_name == '14':
                #     amt_percent = 5
                # print('amt_percent:',amt_percent)
                # #if amt percent is 1,2,3,5
                # if amt_percent:
                #     total_item +=1
                #     # calculate total paid
                #     total_wht_amount += line.credit
                #     # print line.credit
                #     # print total_wht_amount
                #     total_amount += (line.credit * 100) / amt_percent

                total_item +=1
                # calculate total paid
                total_wht_amount += line.credit
                # print line.credit
                # print total_wht_amount
                total_amount += line.amount_before_tax



        else:
            total_amount = 0
            total_wht_amount = 0

        total_page = int(math.ceil(total_item / 6.0))


        return {
            'total_amount': total_amount,
            'total_wht_amount': total_wht_amount,
            'total_item': total_item,
            'total_page':total_page,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        print('666666666')
        print('cccccccccccccccc')
        company_id = self.env.company
        # docs = self.env['account.move.line'].search([('name','=','Output VAT'),('company_id','=',1)])
        header_info = self._get_header_info(data['date_from'], data['date_to'], company_id)
        tax_info = self._get_tax_month(data['date_from'], data['date_to'], company_id,
                                       data['report_type'])
        print('tax_info:',tax_info)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move.line',
            'data': data,
            'get_header_info':header_info,
            'get_tax_info':tax_info,
            'company_id': company_id,
            # 'docs': docs,
        }

