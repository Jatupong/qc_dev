# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime,timedelta,date

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT



class report_sale_tax_report(models.AbstractModel):
    _name = 'report.itaas_std_tax_report.purchase_tax_report_id'

    def _get_data_vat_exmpted(self, data, domain):
        print('Caseeeeeeeeeee_vat_exmpted', domain)
        doc = []
        docs = self.env['account.move.line'].search(domain)
        print('DOCSSSSS_EXMPTED:',doc)
        print('DOCSSSSS_EXMPTED_57681:',docs)
        for move_line_id in docs:
            if not move_line_id.tax_ids.name == 'Input VAT Exempted':
                continue
                print('if not move_line_id.tax_ids.is_tax_exempted:')
            if move_line_id.tax_ids and move_line_id.tax_ids.amount != 0.00:
                continue
                print('if move_line_id.tax_ids and move_line_id.tax_ids.amount != 0.00:')
            if move_line_id.date_vat_new:
                date_t2 = move_line_id.date_vat_new
                print('move_line_id.date_vat_new:')
            else:
                date_t2 = move_line_id.tax_inv_date
            ref = move_line_id.ref
            if move_line_id.move_id.move_type == 'in_refund':
                if move_line_id.tax_base_amount:
                    amount_untaxed = move_line_id.tax_base_amount * (-1)
                elif move_line_id.amount_before_tax:
                    amount_untaxed = move_line_id.amount_before_tax * (-1)
                else:
                    amount_untaxed = abs(move_line_id.balance) * (-1)
            else:
                if move_line_id.tax_base_amount:
                    print('Case_1')
                    amount_untaxed = move_line_id.tax_base_amount
                elif move_line_id.amount_before_tax:
                    print('CASE_2')
                    amount_untaxed = move_line_id.amount_before_tax
                else:
                    print('CASE_3')
                    amount_untaxed = abs(move_line_id.balance)
            amount_tax = 0.00
            amount_total = amount_untaxed + amount_tax
            print('amount_untaxedaaaaaaaaaaaaaaaaaaaaaaa:', amount_untaxed)
            move_line_ids = {
                'date': date_t2,
                'ref': ref or 'False',
                'partner': move_line_id.partner_id,
                'vat': move_line_id.partner_id.vat,
                'branch': move_line_id.partner_id.branch_no,
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                'debit': 0,
                'credit': 0,
                'note': move_line_id.move_id.name,
                'type': move_line_id.move_id.move_type,
                'move_id': move_line_id.move_id,
                'state': move_line_id.move_id.state,
            }
            doc.append(move_line_ids)
        return doc
    def _get_data_vat_0(self,data,domain):
        print('Caseeeeeeeeeee_vat_0',domain)
        doc = []
        docs = self.env['account.move.line'].search(domain)
        print('______docs:', docs)
        for move_line_id in docs:
            print('move_line_id_VAT_0:', move_line_id)
            if (move_line_id.tax_ids and move_line_id.tax_ids.amount != 0.00) or move_line_id.tax_ids.is_tax_exempted:
                print('CONTINUTEEEEEEEE:')
                continue
            if move_line_id.date_vat_new:
                date_t2 = move_line_id.date_vat_new
            else:
                date_t2 = move_line_id.tax_inv_date
            ref = move_line_id.ref
            if move_line_id.move_id.move_type == 'in_refund':
                if move_line_id.tax_base_amount:
                    amount_untaxed = move_line_id.tax_base_amount * (-1)
                elif move_line_id.amount_before_tax:
                    amount_untaxed = move_line_id.amount_before_tax * (-1)
                else:
                    amount_untaxed = abs(move_line_id.balance) * (-1)
            else:
                if move_line_id.tax_base_amount:
                    print('Case_1')
                    amount_untaxed = move_line_id.tax_base_amount
                elif move_line_id.amount_before_tax:
                    print('CASE_2')
                    amount_untaxed = move_line_id.amount_before_tax
                else:
                    print('CASE_3')
                    amount_untaxed = abs(move_line_id.balance)
            amount_tax = 0.00
            amount_total = amount_untaxed + amount_tax
            print('amount_untaxedaaaaaaaaaaaaaaaaaaaaaaa:', amount_untaxed)
            move_line_ids = {
                'date': date_t2,
                'ref': ref or 'False',
                'partner': move_line_id.partner_id,
                'vat': move_line_id.partner_id.vat,
                'branch': move_line_id.partner_id.branch_no,
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                'debit': 0,
                'credit': 0,
                'note': move_line_id.move_id.name,
                'type': move_line_id.move_id.move_type,
                'move_id': move_line_id.move_id,
                'state': move_line_id.move_id.state,
            }
            doc.append(move_line_ids)
        return doc
    def _get_data_vat_7(self,data,domain):
        print('_get_data_vat_7')
        doc = []
        tax = self.env['account.tax'].search([('tax_report', '=', True),
                                              ('amount', '=', 7.0000),
                                              ('type_tax_use', '=', 'purchase')])
        print('tax:', tax)
        account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
        docs = self.env['account.move.line'].search(domain)
        print('docsdddddddddddddd:',docs)

        for move_line_id in docs.filtered(lambda x: x.account_id in account_ids):
            if move_line_id.date_vat_new:
                date_t2 = move_line_id.date_vat_new
            else:
                date_t2 = move_line_id.tax_inv_date
            ref = move_line_id.ref
            if move_line_id.move_id.move_type == 'in_refund':
                if move_line_id.tax_base_amount:
                    amount_untaxed = move_line_id.tax_base_amount * (-1)
                elif move_line_id.amount_before_tax:
                    amount_untaxed = move_line_id.amount_before_tax * (-1)
                else:
                    amount_untaxed = abs(move_line_id.balance) * (100 / 7) * (-1)

                if move_line_id.debit:
                    amount_tax = move_line_id.debit * (-1)
                else:
                    amount_tax = move_line_id.credit * (-1)
            else:
                if move_line_id.tax_base_amount:
                    amount_untaxed = move_line_id.tax_base_amount
                elif move_line_id.amount_before_tax:
                    amount_untaxed = move_line_id.amount_before_tax
                else:
                    amount_untaxed = abs(move_line_id.balance) * (100 / 7)

                if move_line_id.debit:
                    amount_tax = move_line_id.debit
                else:
                    amount_tax = move_line_id.credit
            amount_total = amount_untaxed + amount_tax
            move_line_ids = {
                'date': date_t2,
                'ref': ref or "False",
                'partner': move_line_id.partner_id,
                'vat': move_line_id.partner_id.vat,
                'branch': move_line_id.partner_id.branch_no,
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                'debit': move_line_id.debit,
                'credit': move_line_id.credit,
                'note': move_line_id.move_id.name,
                'type': move_line_id.move_id.move_type,
                'move_id': move_line_id.move_id,
                'state': move_line_id.move_id.state,
            }
            doc.append(move_line_ids)
        return doc
    def _get_result_purchase_tax(self,data):
        print('_get_result_purchase_tax',data)
        doc = []
        # Case ปรกติ ====================================================ิ
        if 'operating_unit' in data and data['operating_unit']:
            print('CASE_1_OU')
            domain = [('account_id.purchase_tax_report', '=', True),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('date_maturity', '=', False),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                      ('operating_unit_id', 'in', data['operating_unit'])]
        else:
            print('CASE_1_NOT_OU')
            domain = [('account_id.purchase_tax_report', '=', True),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('date_maturity', '=', False),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
        if data['type_vat'] == 'vat_0':
            print('Case_vat_0')
            domain = [('tax_ids', '!=', False),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            doc += self._get_data_vat_0(data,domain)
            print('doc_VAT_0:',doc)
        elif data['type_vat'] == 'vat_7':
            print('Case_vat_7')
            doc += self._get_data_vat_7(data,domain)
        elif data['type_vat'] == 'vat_exmpted':
            print('vat_exmpted_vat_exmpted')
            domain = [('tax_ids', '!=', False),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            doc += self._get_data_vat_exmpted(data, domain)
            print('doc_doc_exmpted:',doc)
        else:
            print('Case_vat_all')
            domain_vat_0 = [('tax_ids', '!=', False),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            domain_exmpted = [('tax_ids', '!=', False),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            doc += self._get_data_vat_0(data,domain_vat_0)
            doc += self._get_data_vat_exmpted(data, domain_exmpted)
            doc += self._get_data_vat_7(data, domain)


        # Case ข้ามเดือน ===================================================
        if 'operating_unit' in data and data['operating_unit']:
            print('CASE_2_OU')
            domain = [('account_id.purchase_tax_report', '=', True),
                      ('date_maturity', '>=', data['date_from']),
                      ('date_maturity', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('date_maturity', '!=', False),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                      ('operating_unit_id', 'in', data['operating_unit'])]
        else:
            print('CASE_2_NOT_OU')
            domain = [('account_id.purchase_tax_report', '=', True),
                      ('date_maturity', '>=', data['date_from']),
                      ('date_maturity', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('date_maturity', '!=', False),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                      ]
        if data['type_vat'] == 'vat_0':
            print('Case_vat_0')
            domain = [('tax_ids', '!=', False),
                      ('date_maturity', '>=', data['date_from']),
                      ('date_maturity', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('date_maturity', '!=', False),
                      ('is_special_tax', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            doc += self._get_data_vat_0(data,domain)
            print('CASE_2_VAT_0',doc)
        elif data['type_vat'] == 'vat_7':
            print('Case_vat_7')
            doc += self._get_data_vat_7(data, domain)
        else:
            print('Case_vat_all')
            domain_vat_0 = [('tax_ids', '!=', False),
                            ('date_maturity', '>=', data['date_from']),
                            ('date_maturity', '<=', data['date_to']),
                            ('move_id.state', '=', 'posted'),
                            ('date_maturity', '!=', False),
                            ('is_special_tax', '=', False),

                            ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))]
            doc += self._get_data_vat_0(data, domain_vat_0)
            doc += self._get_data_vat_7(data, domain)

        # Case กลับรายการ ===================================================
        if 'operating_unit' in data and data['operating_unit']:
            print('CASE_2_OU')
            domain = [('account_id.purchase_tax_report', '=',True),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('is_special_tax', '=', True),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                      ('operating_unit_id', 'in', data['operating_unit'])
                      ]
            if data['type_vat'] == 'vat_7':
                doc += self._get_data_vat_7(data, domain)
        else:
            print('CASE_2_NOT_OU')
            domain = [('account_id.purchase_tax_report', '=',True),
                      ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                      ('is_special_tax', '=', True)
                      ]
            if data['type_vat'] == 'vat_7':
                doc += self._get_data_vat_7(data, domain)
            elif not data['type_vat']:
                doc += self._get_data_vat_7(data, domain)
        if doc:
            doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        return doc

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values_Purchase')
        company_id = self.env.company
        result = self._get_result_purchase_tax(data)
        print('result_result',result)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': result,
            'company_id': company_id,
            'data': data,
        }
