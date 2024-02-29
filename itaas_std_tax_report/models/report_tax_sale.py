# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime,timedelta,date

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT



class report_sale_tax_report(models.AbstractModel):
    _name = 'report.itaas_std_tax_report.sale_tax_report_id'


    def _get_result_sale_tax(self,data):
        domain = [('tax_invoice_date', '>=', data['date_from']),
                  ('tax_invoice_date', '<=', data['date_to']),
                  ('state', '=', 'posted'),
                  ('move_type', 'in', ('out_invoice', 'out_refund')),
                  ]
        docs = self.env['account.move'].search(domain)
        return docs
    def _get_result_sale_tax_entry(self,data):
        domain = [('tax_invoice_date', '>=', data['date_from']),
                  ('tax_invoice_date', '<=', data['date_to']),
                  ('state', '=', 'posted'),
                  ('move_type', '=', 'entry'),
                  ]
        docs = self.env['account.move'].search(domain)

        return docs

    def _get_data_sale_tax_filter(self,move_ids,type):
        print('_get_data_sale_tax_filter')
        data_temp = []
        print('teeeeeeeeeype:',type)
        if type == 'vat_0':
            print('vat_0')
            tax_ids = self.env['account.tax'].search([('tax_report', '=', True),
                                                  ('amount', '=', 0),
                                                  ('is_tax_exempted', '=', False),
                                                  ('type_tax_use', '=', 'sale')])
            print('move_idsss_vat_0:',move_ids)
            for move_id in move_ids:
                print('Move_id_vat_0',move_id)
                for tax_id in tax_ids:
                    print('tax_id_vat_0:',tax_id)
                    if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax_id.id):
                        print('WRITE_VAT_0:',move_id)
                        date = move_id.tax_invoice_date
                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = move_id.amount_untaxed
                            amount_tax = move_id.amount_tax
                            amount_total = move_id.amount_total
                            untaxed_amount_after_discount = move_id.amount_untaxed
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)], limit=1)
                            print('rate:', rate)
                            rate = rate.rate
                            amount_untaxed = move_id.amount_untaxed / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = move_id.amount_total / rate
                            untaxed_amount_after_discount = move_id.amount_untaxed / rate
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': move_id.partner_id.name,
                            'untaxed_amount_after_discount': untaxed_amount_after_discount,
                            'vat': move_id.partner_id.vat,
                            'branch': move_id.partner_id.branch_no,
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_total,
                            'move_id': move_id,
                            'state': move_id.state,
                            'type': move_id.move_type,
                            'invoice_line': move_id.invoice_line_ids,
                        }
                        data_temp.append(move_ids)
        elif type == 'vat_7':
            print('vat_7')
            tax_ids = self.env['account.tax'].search([('tax_report', '=', True),
                                                  ('amount', '=', 7),
                                                  ('type_tax_use', '=', 'sale')])
            for move_id in move_ids:
                for tax_id in tax_ids:
                    if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax_id.id):
                        date = move_id.tax_invoice_date
                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = move_id.amount_untaxed
                            amount_tax = move_id.amount_tax
                            amount_total = move_id.amount_total
                            untaxed_amount_after_discount = move_id.amount_untaxed
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date),
                                 ('company_id', '=', self.env.company.id)], limit=1)
                            rate = rate.rate
                            amount_untaxed = move_id.amount_untaxed / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = move_id.amount_total / rate
                            untaxed_amount_after_discount = move_id.amount_untaxed / rate
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': move_id.partner_id.name,
                            'untaxed_amount_after_discount': untaxed_amount_after_discount,
                            'vat': move_id.partner_id.vat,
                            'branch': move_id.partner_id.branch_no,
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_total,
                            'move_id': move_id,
                            'state': move_id.state,
                            'type': move_id.move_type,
                            'invoice_line': move_id.invoice_line_ids,
                        }
                        data_temp.append(move_ids)
        elif type == 'vat_exmpted':
            print('vat_exmpted')
            tax = self.env['account.tax'].search([('is_tax_exempted', '=', True),
                                                  ('amount', '=', 0),
                                                  ('is_tax_exempted', '=', True),
                                                  ('type_tax_use', '=', 'sale')])
            print('tax_tax:', tax)
            for move_id in move_ids:
                print('move_id_vat_0:', move_id)
                # if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax.id or not a.tax_ids):
                # if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids or a.tax_ids.id == tax.id):
                if move_id.invoice_line_ids.filtered(lambda a: a.product_id and not a.tax_ids or a.tax_ids.name == 'Output VAT Exempted'):
                    print('move_id:', move_id.id)
                    if move_id.journal_id.type_vat == 'tax':
                        date = move_id.tax_invoice_date
                    elif move_id.journal_id.type_vat == 'not_deal':
                        date = move_id.tax_invoice_date
                    else:
                        date = move_id.tax_invoice_date

                    if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                        amount_untaxed = move_id.amount_untaxed
                        amount_tax = move_id.amount_tax
                        amount_total = move_id.amount_total
                        untaxed_amount_after_discount = move_id.amount_untaxed
                    else:
                        rate = self.env['res.currency.rate'].search(
                            [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                            limit=1)
                        print('rate:', rate)
                        rate = rate.rate
                        amount_untaxed = move_id.amount_untaxed / rate
                        amount_tax = move_id.amount_tax / rate
                        amount_total = move_id.amount_total / rate
                        untaxed_amount_after_discount = move_id.amount_untaxed / rate
                    move_ids = {
                        'date': date.strftime("%d/%m/%Y"),
                        'name': move_id.tax_inv_number or move_id.name,
                        'partner': move_id.partner_id.name,
                        'untaxed_amount_after_discount': untaxed_amount_after_discount,
                        'vat': move_id.partner_id.vat,
                        'branch': move_id.partner_id.branch_no,
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'move_id': move_id,
                        'state': move_id.state,
                        'type': move_id.move_type,
                        'invoice_line': move_id.invoice_line_ids,
                    }
                    data_temp.append(move_ids)
                    # print('doc_last:', doc)
        elif type == 'entry':
            print('Type_entryyyyyyyy',move_ids)
            for move_id in move_ids:
                print('move_id_entryy:',move_id)
                sale_tax_line = move_id.line_ids.filtered(lambda a: a.account_id.sale_tax_report)
                print('sale_tax_lineซ',sale_tax_line)
                if not sale_tax_line:
                    print('CONTINUEEEEEEEEEEEE:')
                    continue
                if move_id.journal_id.type_vat == 'tax':
                    date = move_id.tax_invoice_date
                elif move_id.journal_id.type_vat == 'not_deal':
                    date = move_id.tax_invoice_date
                else:
                    date = move_id.tax_invoice_date
                print('BEFOREEEEEEEEEEEE')
                for move_line in sale_tax_line:
                    amount_untaxed = 0
                    amount_tax = 0
                    amount_total = 0
                    print('move_line_credit',move_line.credit)
                    print('move_line_debit',move_line.debit)
                    if not move_line.credit and not move_line.debit:
                        continue
                    if move_line.credit:
                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = move_line.tax_base_amount or move_line.amount_before_tax
                            amount_tax = move_line.credit
                            amount_total = amount_untaxed + amount_tax
                        else:
                            rate = self.env['res.currency.rate'].search([('name', '<=', move_id.tax_invoice_date), ('company_id', '=', self.env.company.id)],limit=1)
                            rate = rate.rate
                            amount_untaxed = move_line.tax_base_amount / rate or move_line.amount_before_tax / rate
                            amount_tax = move_line.credit / rate
                            amount_total = (amount_untaxed + amount_tax) / rate
                    elif move_line.debit:
                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = abs(move_line.tax_base_amount) * (-1) or abs(move_line.amount_before_tax) * (-1)
                            amount_tax = abs(move_line.debit) * (-1)
                            amount_total = abs(amount_untaxed + amount_tax) * (-1)
                        else:
                            rate = self.env['res.currency.rate'].search([('name', '<=', move_id.tax_invoice_date), ('company_id', '=', self.env.company.id)],limit=1)
                            rate = rate.rate
                            amount_untaxed = abs(move_line.tax_base_amount / rate) * (-1) or abs(move_line.amount_before_tax / rate) * (-1)
                            amount_tax = abs(move_line.debit / rate) * (-1)
                            amount_total = abs((amount_untaxed + amount_tax) / rate) * (-1)
                    move_ids = {
                        'date': date.strftime("%d/%m/%Y"),
                        'name': move_id.tax_inv_number or move_id.name,
                        'partner': move_id.partner_id.name or move_line.partner_id.name or 'Cash',
                        'vat': move_id.partner_id.vat or move_line.partner_id.vat,
                        'branch': move_id.partner_id.branch_no or move_line.partner_id.branch_no,
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'move_id': move_id,
                        'state': move_id.state,
                        'type': move_id.move_type,
                    }
                    data_temp.append(move_ids)
        else:
            print('vat_all')
            tax_ids = self.env['account.tax'].search([('tax_report', '=',False),
                                                      ('amount', '=', 7),
                                                      ('is_tax_not_due', '=', True),
                                                      ('type_tax_use', '=', 'sale')],limit=1)

            for move_id in move_ids:
                if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax_ids.id):
                    continue
                print('move_idmove_id',move_id)
                date = move_id.tax_invoice_date
                if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                    amount_untaxed = move_id.amount_untaxed
                    amount_tax = move_id.amount_tax
                    amount_total = move_id.amount_total
                    untaxed_amount_after_discount = move_id.amount_untaxed
                else:
                    rate = self.env['res.currency.rate'].search([('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)], limit=1)
                    rate = rate.rate
                    print('rate:', rate)
                    amount_untaxed = move_id.amount_untaxed / rate
                    amount_tax = move_id.amount_tax / rate
                    amount_total = move_id.amount_total / rate
                    untaxed_amount_after_discount = move_id.amount_untaxed / rate
                move_ids = {
                    'date': date.strftime("%d/%m/%Y"),
                    'name': move_id.tax_inv_number or move_id.name,
                    'partner': move_id.partner_id.name,
                    'untaxed_amount_after_discount': untaxed_amount_after_discount,
                    'vat': move_id.partner_id.vat,
                    'branch': move_id.partner_id.branch_no,
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_total,
                    'move_id': move_id,
                    'state': move_id.state,
                    'type': move_id.move_type,
                    'invoice_line': move_id.invoice_line_ids,
                }
                data_temp.append(move_ids)



        return data_temp

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values_sale')
        print('Data:',data)
        data_result = []
        company_id = self.env.company
        if 'operating_unit' in data and data['operating_unit']:
            print('Case Ou')
        else:
            print('Case Not Ou')
            result = self._get_result_sale_tax(data)
            print('dataaaaaa:',data)
            if 'vat_0' in data and data['type_vat'] == 'vat_0':
                is_vat = 'vat_0'
                print('Case_vat_0_sale')
                data_result = self._get_data_sale_tax_filter(result,is_vat)
            elif 'vat_7' in data and data['type_vat'] == 'vat_7':
                is_vat = 'vat_7'
                print('Case_vat_7_sale')
                data_result = self._get_data_sale_tax_filter(result,is_vat)
            elif 'vat_exmpted' in data and data['type_vat'] == 'vat_exmpted':
                is_vat = 'vat_exmpted'
                print('Case_vat_exmpted_sale')
                data_result = self._get_data_sale_tax_filter(result,is_vat)
            else:
                print('Case_all_vat_sale')
                is_vat = 'vat_all'
                data_result = self._get_data_sale_tax_filter(result,is_vat)
            if 'vat_7' in data and data['type_vat'] == 'vat_7' or not data['type_vat']:
                is_vat = "entry"
                result = self._get_result_sale_tax_entry(data)
                print('================== result:',result)
                data_result += self._get_data_sale_tax_filter(result, is_vat)
        print('data_resultttttttttttttttttttttt',data_result)
        if not data_result:
            raise UserError(_('Document is empty.'))
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': data_result,
            'company_id': company_id,
            'data': data,
        }
