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


class account_move(models.Model):
    _inherit = 'account.move'


    def company_data(self):
        print('vvvvvv')

    def purchase_data(self):
        # print(self.date_from)
        data_purchase = {}
        amount = 0
        purchase_tax = self.env['account.move.line'].search(
            [('account_id.purchase_tax_report', '=', True), ('move_id.state', '!=', 'draft')])
        # print(purchase_tax.tax_base_amount)
        # purchase_tax_last = purchase_tax[len(purchase_tax) - 1]
        if purchase_tax.mapped('debit'):
            amount = sum(purchase_tax.mapped('debit')) * (-1)
        else:
            amount = sum(purchase_tax.mapped('credit'))
        amount_before_tax = sum(purchase_tax.mapped('amount_before_tax'))
        data_purchase = {
            'amount': abs(amount),
            'amount_before_tax': amount_before_tax,
            # 'purchase_tax_last': purchase_tax_last,
        }
        return data_purchase

    def sale_data(self):
        data_sale = {}
        amount = 0
        sale_tax = self.env['account.move.line'].search(
            [('account_id.sale_tax_report', '=', True), ('move_id.state', '!=', 'draft')])
        if sale_tax.mapped('debit'):
            amount = sum(sale_tax.mapped('debit')) * (-1)
        else:
            amount = sum(sale_tax.mapped('credit'))
        amount_before_tax = sum(sale_tax.mapped('amount_before_tax'))
        data_sale = {
            'amount': abs(amount),
            'amount_before_tax': amount_before_tax,
        }
        return data_sale



class pnd30_report_tax(models.TransientModel):
    _name = 'pnd30.report.tax'

    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)
    fax_for = fields.Boolean(string='ยื่นปรกติ')
    fax_1 = fields.Boolean(string='แยกยื่น')
    fax_2 = fields.Boolean(string='ยื่นรวม')
    previous_balance = fields.Float(string='ภาษีที่ชำระเกินยกมา')



    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     model = self.env.context.get('active_model')
    #     docs = self.env[model].browse(self.env.context.get('active_id'))
    #     print(docids)
    #     print('=vvv=v=v=v==v')
    #     doc_model = 'account.move'
    #     domain = []
    #     if data:
    #         print('vvvv')
    #
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': doc_model,
    #         'data': data,
    #         'docs': docs,
    #     }
    #     return docargs

    def print_pnd30_report(self):
        data = {'date_from': self.date_from, 'date_to': self.date_to,'vat_0':False}
        print('================')
        print(data)
        print('================')

        if data['date_from'] and data['date_to'] :
            return self.env.ref('itaas_print_tax_report.action_tax_30_report_id').report_action(self, data=data)

class report_report_pnd30_id(models.AbstractModel):
    _name = 'report.itaas_print_tax_report.report_pnd30_id'


    def sale_data(self,data,company_id):
        print('============sale_data=======================')
        company_id = self.env.company
        sum_vat_7_and_0 = amount_0 = amount_sum_4 = amount_sum_5 = 0
        data = {'date_from': data['date_from'], 'date_to': data['date_to'], 'report_type':'sale', 'tax_id': False, 'company_id': company_id}
        docs = self.env['report.itaas_print_tax_report.sale_tax_report_id']._get_report_values(self,data=data)
        print('report_values:',docs)
        for move_id in docs['docs']:
            if move_id['state'] != 'cancel':
                if move_id['type'] == 'out_refund':
                    if move_id['untaxed_amount_after_discount']:
                        sum_vat_7_and_0 += move_id['untaxed_amount_after_discount'] * (-1)
                        amount_sum_5 += move_id['amount_tax'] * (-1)
                    else:
                        sum_vat_7_and_0 += move_id['amount_untaxed'] * (-1)
                        amount_sum_5 += move_id['amount_tax'] * (-1)

                else:
                    # if move_id['untaxed_amount_after_discount']:
                    #     sum_vat_7_and_0 += move_id['untaxed_amount_after_discount']
                    #     amount_sum_5 += move_id['amount_tax']

                    # else:
                    sum_vat_7_and_0 += move_id['amount_untaxed']
                    amount_sum_5 += move_id['amount_tax']

            # if move_id['invoice_line'][0].tax_ids.amount == 0:
            #     if move_id['state'] != 'cancel':
            #         if move_id['type'] == 'out_refund':
            #             if move_id['untaxed_amount_after_discount']:
            #                 amount_0 += move_id['untaxed_amount_after_discount'] * (-1)
            #             else:
            #                 amount_0 += move_id['amount_untaxed'] * (-1)
            #         else:
            #             if move_id['untaxed_amount_after_discount']:
            #                 amount_0 += move_id['untaxed_amount_after_discount']
            #             else:
            #                 amount_0 += move_id['amount_untaxed']
        amount_sum_4 = sum_vat_7_and_0 - amount_0
        data_sale = {
            'amount_untaxed_7_and_0':  sum_vat_7_and_0,
            'amount_0': amount_0,
            'amount_sum_4' : amount_sum_4,
            'amount_sum_5' : amount_sum_5,
        }
        return data_sale


    def purchase_data(self,data,company_id):
        print('purchase_date')
        data_purchase = {}
        amount = 0
        amount_total_7_0 = amount_total_tax = 0
        data = {'date_from': data['date_from'], 'date_to': data['date_to'], 'report_type': 'purchase', 'tax_id': False,
                'company_id': company_id}
        docs = self.env['report.itaas_print_tax_report.purchase_tax_report_id']._get_report_values(self, data=data)
        for move_id in docs['docs']:
            print('move_id_purchase_line:',move_id)
            if move_id['type'] == 'in_refund':
                if move_id['debit']:
                    amount_total_tax += move_id['debit'] * (-1)
                else:
                    amount_total_tax += move_id['credit'] * (-1)
                print('==============REFUND==========')
                print('debit:', move_id['debit'])
                print('debit:', move_id['credit'])
                print('amount_total_tax_refund', amount_total_tax)
                if move_id['amount_untaxed']:
                    amount_total_7_0 += move_id['amount_untaxed']
                else:
                    if move_id['debit']:
                        amount_total_7_0 += (move_id['debit'] / 0.07)
                    elif move_id['credit']:
                        amount_total_7_0 += (move_id['credit'] / 0.07)
            else:

                if move_id['debit']:
                    amount_total_tax += move_id['debit']
                else:
                    amount_total_tax += move_id['credit']
                print('==============+NO REFUND==========')
                print('debit:',move_id['debit'])
                print('debit:',move_id['credit'])
                print('amount_total_tax_no_refund',amount_total_tax)
                if move_id['amount_untaxed']:
                    amount_total_7_0 += move_id['amount_untaxed']
                else:
                    if move_id['debit']:
                        amount_total_7_0 += (move_id['debit'] / 0.07)
                    elif move_id['credit']:
                        amount_total_7_0 += (move_id['credit'] / 0.07)

        data_purchase = {
            'amount_before_tax': amount_total_7_0,
            'amount_vat': amount_total_tax,
        }

        return data_purchase


    @api.model
    def _get_report_values(self, docids, data=None):
        print('GET_REPORT_VALUESE')
        # company_id = self.env.user.company_id
        company_id = self.env.company
        print('data',data)
        print(company_id.name)
        print(company_id.zip)
        date_to = data['date_to']
        purchase = self.purchase_data(data,company_id)
        sale = self.sale_data(data,company_id)

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        print('purchase:',purchase)
        print('sale:',sale)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'company_id': company_id,
            'purchase': purchase,
            'sale': sale,
            'data': data,
            'date_to':date_to,
        }





