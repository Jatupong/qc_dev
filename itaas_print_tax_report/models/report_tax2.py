# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime,timedelta,date

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT



class report_sale_tax_report(models.AbstractModel):
    _name = 'report.itaas_print_tax_report.sale_tax_report_id2'

    def get_partner_name(self,move_id):
        name = move_id.partner_id.name
        return name


    def get_amount_multi_currency(self,move_id):
        total_amount = 0.0
        tax_amount = 0.0
        for line in move_id.line_ids:
            total_amount += abs(line.debit)
            if line.account_id.sale_tax_report:
                tax_amount += abs(line.balance)
        return total_amount, tax_amount

    @api.model
    def _get_report_values(self, docids, data=None):
        print ('------_get_report_values ----> sales---')
        print('data:',data)
        company_id = self.env.company
        operating_unit_id = False
        docs = False
        check_ou_for_pdf = []
        move_ids = {}
        doc = []
        if 'operating_unit' in data and data['operating_unit']:
            for ou_id in data['operating_unit']:
                obj_ou_id = self.env["operating.unit"].search([("id", "=", ou_id)])
                check_ou_for_pdf.append(obj_ou_id.name)
            print('IS operating_unit')
            domain = [('tax_invoice_date','>=',data['date_from']),('tax_invoice_date','<=',data['date_to']),
                      ('state','in',('posted','cancel')),('move_type','in',('out_invoice','out_refund')),
                      ('operating_unit_id','in',(data['operating_unit']),
                       ('is_manual_cn','=',False))]
            docs = self.env['account.move'].search(domain)
            print('docs:', docs)
            date = datetime.today()
            amount_untaxed = 0
            amount_tax = 0
            amount_total = 0
            sum_untaxed = 0
            untaxed_amount_after_discount = 0
            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'sale')])
                print('taxxxxxxxxxxxxxx:', tax)
                for move_id in docs:
                    print('move_id:', move_id)
                    all_tax_ids = len(move_id.invoice_line_ids.mapped('tax_ids'))
                    if all_tax_ids == 1:
                        if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax.id and a.tax_ids.is_tax_not_due):
                            if move_id.adjust_move_id:
                                print('move_id:', move_id.id)
                                if move_id.journal_id.type_vat == 'tax':
                                    date = move_id.tax_invoice_date
                                elif move_id.journal_id.type_vat == 'not_deal':
                                    date = move_id.tax_invoice_date
                                else:
                                    date = move_id.tax_invoice_date

                                if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                    print('aaaaa')

                                    amount_untaxed = move_id.amount_untaxed
                                    amount_tax = move_id.amount_tax
                                    amount_total = move_id.amount_total
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                                else:
                                    rate = self.env['res.currency.rate'].search(
                                        [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                        limit=1)
                                    print('rate:', rate)
                                    rate = rate.rate
                                    amount_untaxed = move_id.amount_untaxed / rate
                                    amount_tax = move_id.amount_tax / rate
                                    amount_total = move_id.amount_total / rate
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                                if len(move_id.invoice_line_ids) >= 2:
                                    sum = 0.0
                                    for i in move_id.invoice_line_ids:
                                        sum = sum + i.quantity
                                        print("ID_quantity", i, ":", i.quantity)
                                elif len(move_id.invoice_line_ids) <= 1:
                                    sum = move_id.invoice_line_ids.quantity
                                if len(move_id.currency_id.rate_ids) >= 2:
                                    company_rate = move_id.currency_id.rate_ids[0].company_rate
                                    print("company_rate!!:", company_rate)
                                elif len(move_id.currency_id.rate_ids) < 2:
                                    company_rate = move_id.currency_id.rate_ids.company_rate
                                    print("company_rate!!!:", company_rate)
                                if company_rate == 0.0:
                                    company_rate = 1.0
                                print("company_rate!!!!:", company_rate)
                                move_ids = {
                                    'date': date.strftime("%d/%m/%Y"),
                                    'name': move_id.tax_inv_number or move_id.name,
                                    'partner': self.get_partner_name(move_id),
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
                                    'ETD': move_id.etd,
                                    'ETA': move_id.eta,
                                    'quantity': sum,
                                    'excrate': move_id.customs_department,
                                    'amount_type': move_id.currency_id.name,
                                    'export_products_id': move_id.export_products_id,
                                    'company_rate': company_rate,
                                }
                                doc.append(move_ids)
                                print('doc_last:', doc)
                        elif move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax.id):
                            print('move_id:', move_id.id)
                            if move_id.journal_id.type_vat == 'tax':
                                date = move_id.tax_invoice_date
                            elif move_id.journal_id.type_vat == 'not_deal':
                                date = move_id.tax_invoice_date
                            else:
                                date = move_id.tax_invoice_date

                            if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                print('aaaaa')
                                amount_untaxed = move_id.amount_untaxed
                                amount_tax = move_id.amount_tax
                                amount_total = move_id.amount_total
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                            else:
                                rate = self.env['res.currency.rate'].search(
                                    [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                    limit=1)
                                print('rate:', rate)
                                rate = rate.rate
                                amount_untaxed = move_id.amount_untaxed / rate
                                amount_tax = move_id.amount_tax / rate
                                amount_total = move_id.amount_total / rate
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                            if len(move_id.invoice_line_ids) >= 2:
                                sum = 0.0
                                for i in move_id.invoice_line_ids:
                                    sum = sum + i.quantity
                                    print("ID_quantity", i, ":", i.quantity)
                            elif len(move_id.invoice_line_ids) <= 1:
                                sum = move_id.invoice_line_ids.quantity
                            if len(move_id.currency_id.rate_ids) >= 2:
                                company_rate = move_id.currency_id.rate_ids[0].company_rate
                                print("company_rate!!:", company_rate)
                            elif len(move_id.currency_id.rate_ids) < 2:
                                company_rate = move_id.currency_id.rate_ids.company_rate
                                print("company_rate!!!:", company_rate)
                            if company_rate == 0.0:
                                company_rate = 1.0
                            print("company_rate!!!!:", company_rate)
                            move_ids = {
                                'date': date.strftime("%d/%m/%Y"),
                                'name': move_id.tax_inv_number or move_id.name,
                                'partner': self.get_partner_name(move_id),
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
                                'ETD': move_id.etd,
                                'ETA': move_id.eta,
                                'quantity': sum,
                                'excrate': move_id.customs_department,
                                'amount_type': move_id.currency_id.name,
                                'export_products_id': move_id.export_products_id,
                                'company_rate': company_rate,
                            }
                            doc.append(move_ids)
                            print('doc_last:', doc)
                    else:
                        print('move_iddddd:', move_id)
                        if move_id.journal_id.type_vat == 'tax':
                            date = move_id.tax_invoice_date
                        elif move_id.journal_id.type_vat == 'not_deal':
                            date = move_id.tax_invoice_date
                        else:
                            date = move_id.tax_invoice_date

                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = (move_id.amount_tax / 7) * 100
                            amount_tax = move_id.amount_tax
                            amount_total = amount_untaxed + amount_tax
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                limit=1)
                            rate = rate.rate
                            print('rate:', rate)
                            amount_untaxed = ((move_id.amount_tax / 7) * 100) / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = (amount_untaxed + amount_tax) / rate
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                        print('move_id.amount_tax_move_id.amount_tax:', (move_id.amount_tax / 7) * 100)
                        print('move_id.amount_tax_move_id.amount_tax:', move_id.amount_tax)
                        if len(move_id.invoice_line_ids) >= 2:
                            sum = 0.0
                            for i in move_id.invoice_line_ids:
                                sum = sum + i.quantity
                                print("ID_quantity", i, ":", i.quantity)
                        elif len(move_id.invoice_line_ids) <= 1:
                            sum = move_id.invoice_line_ids.quantity
                        if len(move_id.currency_id.rate_ids) >= 2:
                            company_rate = move_id.currency_id.rate_ids[0].company_rate
                            print("company_rate!!:", company_rate)
                        elif len(move_id.currency_id.rate_ids) < 2:
                            company_rate = move_id.currency_id.rate_ids.company_rate
                            print("company_rate!!!:", company_rate)
                        if company_rate == 0.0:
                            company_rate = 1.0
                        print("company_rate!!!!:", company_rate)
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': self.get_partner_name(move_id),
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
                            'ETD': move_id.etd,
                            'ETA': move_id.eta,
                            'quantity': sum,
                            'excrate': move_id.customs_department,
                            'amount_type': move_id.currency_id.name,
                            'export_products_id': move_id.export_products_id,
                            'company_rate': company_rate,
                        }
                        doc.append(move_ids)
            else:
                print('======TAX_ID_FALSE========')
                for move_id in docs:
                    all_tax_ids = len(move_id.invoice_line_ids.mapped('tax_ids'))
                    if all_tax_ids == 1:
                        if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids and a.tax_ids.is_tax_not_due):
                            print('is_tax_not_due:')
                            if move_id.adjust_move_id:
                                if move_id.journal_id.type_vat == 'tax':
                                    date = move_id.tax_invoice_date
                                elif move_id.journal_id.type_vat == 'not_deal':
                                    date = move_id.tax_invoice_date
                                else:
                                    date = move_id.tax_invoice_date
                                print('amount_type !!: ', move_id.currency_id.name)
                                if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                    amount_type = move_id.currency_id.name
                                    # print('amount_type : ',move_id.currency_id.name)
                                    amount_untaxed = move_id.amount_untaxed
                                    amount_tax = move_id.amount_tax
                                    amount_total = move_id.amount_total
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                                else:
                                    rate = self.env['res.currency.rate'].search(
                                        [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                        limit=1)
                                    rate = rate.rate
                                    print('rate:', rate)
                                    amount_untaxed = move_id.amount_untaxed / rate
                                    amount_tax = move_id.amount_tax / rate
                                    amount_total = move_id.amount_total / rate
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                                if len(move_id.invoice_line_ids) >= 2:
                                    sum = 0.0
                                    for i in move_id.invoice_line_ids:
                                        sum = sum + i.quantity
                                        print("ID_quantity", i, ":", i.quantity)
                                elif len(move_id.invoice_line_ids) <= 1:
                                    sum = move_id.invoice_line_ids.quantity
                                if len(move_id.currency_id.rate_ids) >= 2:
                                    company_rate = move_id.currency_id.rate_ids[0].company_rate
                                    print("company_rate!!:", company_rate)
                                elif len(move_id.currency_id.rate_ids) < 2:
                                    company_rate = move_id.currency_id.rate_ids.company_rate
                                    print("company_rate!!!:", company_rate)
                                if company_rate == 0.0:
                                    company_rate = 1.0
                                print("company_rate!!!!:", company_rate)
                                move_ids = {
                                    'date': date.strftime("%d/%m/%Y"),
                                    'name': move_id.tax_inv_number or move_id.name,
                                    'partner': self.get_partner_name(move_id),
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
                                    'ETD': move_id.etd,
                                    'ETA': move_id.eta,
                                    'quantity': sum,
                                    'excrate': move_id.customs_department,
                                    'amount_type': move_id.currency_id.name,
                                    'export_products_id': move_id.export_products_id,
                                    'company_rate': company_rate,
                                }

                                doc.append(move_ids)
                        elif move_id.invoice_line_ids.filtered(lambda a: a.tax_ids):
                            print('is_tax_not_due:')
                            if move_id.journal_id.type_vat == 'tax':
                                date = move_id.tax_invoice_date
                            elif move_id.journal_id.type_vat == 'not_deal':
                                date = move_id.tax_invoice_date
                            else:
                                date = move_id.tax_invoice_date

                            if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                amount_type = move_id.currency_id.name
                                print('amount_type : ', amount_type)
                                amount_untaxed = move_id.amount_untaxed
                                amount_tax = move_id.amount_tax
                                amount_total = move_id.amount_total
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                            else:
                                rate = self.env['res.currency.rate'].search(
                                    [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                    limit=1)
                                rate = rate.rate
                                print('rate:', rate)
                                amount_untaxed = move_id.amount_untaxed / rate
                                amount_tax = move_id.amount_tax / rate
                                amount_total = move_id.amount_total / rate
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                            if len(move_id.invoice_line_ids) >= 2:
                                sum = 0.0
                                for i in move_id.invoice_line_ids:
                                    sum = sum + i.quantity
                                    print("ID_quantity", i, ":", i.quantity)
                            elif len(move_id.invoice_line_ids) <= 1:
                                sum = move_id.invoice_line_ids.quantity
                            if len(move_id.currency_id.rate_ids) >= 2:
                                company_rate = move_id.currency_id.rate_ids[0].company_rate
                                print("company_rate!!:", company_rate)
                            elif len(move_id.currency_id.rate_ids) < 2:
                                company_rate = move_id.currency_id.rate_ids.company_rate
                                print("company_rate!!!:", company_rate)
                            if company_rate == 0.0:
                                company_rate = 1.0
                            print("company_rate!!!!:", company_rate)
                            move_ids = {
                                'date': date.strftime("%d/%m/%Y"),
                                'name': move_id.tax_inv_number or move_id.name,
                                'partner': self.get_partner_name(move_id),
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
                                'ETD': move_id.etd,
                                'ETA': move_id.eta,
                                'quantity': sum,
                                'excrate': move_id.customs_department,
                                'amount_type': move_id.currency_id.name,
                                'export_products_id': move_id.export_products_id,
                                'company_rate': company_rate,
                            }
                            doc.append(move_ids)
                    else:
                        print('move_iddddd:', move_id)
                        if move_id.journal_id.type_vat == 'tax':
                            date = move_id.tax_invoice_date
                        elif move_id.journal_id.type_vat == 'not_deal':
                            date = move_id.tax_invoice_date
                        else:
                            date = move_id.tax_invoice_date

                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_type = move_id.currency_id.name
                            print('amount_type : ', amount_type)
                            amount_untaxed = (move_id.amount_tax / 7) * 100
                            amount_tax = move_id.amount_tax
                            amount_total = amount_untaxed + amount_tax
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                limit=1)
                            rate = rate.rate
                            print('rate:', rate)
                            amount_untaxed = ((move_id.amount_tax / 7) * 100) / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = (amount_untaxed + amount_tax) / rate
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                        print('move_id.amount_tax_move_id.amount_tax:', (move_id.amount_tax / 7) * 100)
                        print('move_id.amount_tax_move_id.amount_tax:', move_id.amount_tax)
                        if len(move_id.invoice_line_ids) >= 2:
                            sum = 0.0
                            for i in move_id.invoice_line_ids:
                                sum = sum + i.quantity
                                print("ID_quantity", i, ":", i.quantity)
                        elif len(move_id.invoice_line_ids) <= 1:
                            sum = move_id.invoice_line_ids.quantity
                        if len(move_id.currency_id.rate_ids) >= 2:
                            company_rate = move_id.currency_id.rate_ids[0].company_rate
                            print("company_rate!!:", company_rate)
                        elif len(move_id.currency_id.rate_ids) < 2:
                            company_rate = move_id.currency_id.rate_ids.company_rate
                            print("company_rate!!!:", company_rate)
                        if company_rate == 0.0:
                            company_rate = 1.0
                        print("company_rate!!!!:", company_rate)
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': self.get_partner_name(move_id),
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
                            'ETD': move_id.etd,
                            'ETA': move_id.eta,
                            'quantity': sum,
                            'excrate': move_id.customs_department,
                            'amount_type': move_id.currency_id.name,
                            'export_products_id': move_id.export_products_id,
                            'company_rate': company_rate,
                        }
                        doc.append(move_ids)

            #  Domain For Journal Entry
            print('DOC _ INVOIE:', doc)

            domain = [('tax_invoice_date', '>=', data['date_from']), ('tax_invoice_date', '<=', data['date_to']),
                      ('state', 'in', ('posted', 'cancel')), ('move_type', '=', 'entry'),
                       ('is_manual_cn','=',False),
                      ('operating_unit_id', 'in', (data['operating_unit']))]
            docs = self.env['account.move'].search(domain)
            print('docs-Journal_entry:', docs)
            for move_id in docs:
                if move_id.journal_id.type_vat == 'tax':
                    date = move_id.tax_invoice_date
                elif move_id.journal_id.type_vat == 'not_deal':
                    date = move_id.tax_invoice_date
                else:
                    date = move_id.tax_invoice_date

                for move_line in move_id.line_ids.filtered(lambda a: a.account_id.sale_tax_report == True):
                    if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                        print('aaaaa')
                        amount_type = move_id.currency_id.name
                        print('amount_type : ', amount_type)
                        amount_untaxed = move_line.tax_base_amount
                        amount_tax = move_line.credit
                        amount_total = move_line.tax_base_amount + move_line.credit

                    else:
                        rate = self.env['res.currency.rate'].search(
                            [('name', '<=', move_id.tax_invoice_date), ('company_id', '=', self.env.company.id)],
                            limit=1)
                        print('rate:', rate)
                        rate = rate.rate
                        amount_untaxed = move_line.tax_base_amount / rate
                        amount_tax = move_line.credit / rate
                        amount_total = (move_line.tax_base_amount + move_line.credit) / rate
                    if move_id.adjust_move_id:
                        name = move_id.tax_inv_number
                    else:
                        name = move_id.name
                    if len(move_id.invoice_line_ids) >= 2:
                        sum = 0.0
                        for i in move_id.invoice_line_ids:
                            sum = sum + i.quantity
                            print("ID_quantity", i, ":", i.quantity)
                    elif len(move_id.invoice_line_ids) <= 1:
                        sum = move_id.invoice_line_ids.quantity
                    if len(move_id.currency_id.rate_ids) >= 2:
                        company_rate = move_id.currency_id.rate_ids[0].company_rate
                        print("company_rate!!:", company_rate)
                    elif len(move_id.currency_id.rate_ids) < 2:
                        company_rate = move_id.currency_id.rate_ids.company_rate
                        print("company_rate!!!:", company_rate)
                    if company_rate == 0.0:
                        company_rate = 1.0
                    print("company_rate!!!!:", company_rate)
                    move_ids = {
                        'date': date.strftime("%d/%m/%Y"),
                        'name': move_id.tax_inv_number or move_id.name,
                        'partner': self.get_partner_name(move_id),
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
                        'ETD': move_id.etd,
                        'ETA': move_id.eta,
                        'quantity': sum,
                        'excrate': move_id.customs_department,
                        'amount_type': move_id.currency_id.name,
                        'export_products_id': move_id.export_products_id,
                        'company_rate': company_rate,
                    }
                    doc.append(move_ids)
            doc.sort(key=lambda k: (k['date'], k['name']))
            return {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'docs': doc,
                'company_id': company_id,
                'data': data,
                'operating_unit':check_ou_for_pdf,
            }
        else:
            print('not operating_unit')
            domain = [('tax_invoice_date', '>=', data['date_from']), ('tax_invoice_date', '<=', data['date_to']),
                       ('is_manual_cn','=',False),
                      ('state', 'in', ('posted', 'cancel')), ('move_type', 'in', ('out_invoice', 'out_refund'))]
            docs = self.env['account.move'].search(domain)

            print('docs_1:',docs)
            print("Debit /Credit note :",docs.is_manual_cn)
            date = datetime.today()
            amount_untaxed = 0
            amount_tax = 0
            amount_total = 0
            sum_untaxed = 0
            untaxed_amount_after_discount = 0

            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'sale')])
                print('taxxxxxxxxxxxxxx:',tax)
                for move_id in docs:
                    print('move_id:',move_id)
                    all_tax_ids = len(move_id.invoice_line_ids.mapped('tax_ids'))
                    if all_tax_ids == 1:
                        if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax.id and a.tax_ids.is_tax_not_due):
                            if move_id.adjust_move_id:
                                print('move_id:',move_id.id)
                                if move_id.journal_id.type_vat == 'tax':
                                    date = move_id.tax_invoice_date
                                elif move_id.journal_id.type_vat == 'not_deal':
                                    date = move_id.tax_invoice_date
                                else:
                                    date = move_id.tax_invoice_date

                                if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                    print('aaaaa')
                                    amount_untaxed = move_id.amount_untaxed
                                    amount_tax = move_id.amount_tax
                                    amount_total = move_id.amount_total
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                                else:
                                    rate = self.env['res.currency.rate'].search(
                                        [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)], limit=1)
                                    print('rate:',rate)
                                    rate = rate.rate
                                    amount_untaxed = move_id.amount_untaxed / rate
                                    amount_tax = move_id.amount_tax / rate
                                    amount_total = move_id.amount_total / rate
                                    untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                                if len(move_id.invoice_line_ids) >= 2:
                                    sum = 0.0
                                    for i in move_id.invoice_line_ids:
                                        sum = sum + i.quantity
                                        print("ID_quantity", i, ":", i.quantity)
                                elif len(move_id.invoice_line_ids) <= 1:
                                    sum = move_id.invoice_line_ids.quantity
                                if len(move_id.currency_id.rate_ids) >= 2:
                                    company_rate = move_id.currency_id.rate_ids[0].company_rate
                                    print("company_rate!!:", company_rate)
                                elif len(move_id.currency_id.rate_ids) < 2:
                                    company_rate = move_id.currency_id.rate_ids.company_rate
                                    print("company_rate!!!:", company_rate)
                                if company_rate == 0.0:
                                    company_rate = 1.0
                                print("company_rate!!!!:", company_rate)
                                move_ids = {
                                    'date': date.strftime("%d/%m/%Y"),
                                    'name': move_id.tax_inv_number or move_id.name,
                                    'partner': self.get_partner_name(move_id),
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
                                    'ETD': move_id.etd,
                                    'ETA': move_id.eta,
                                    'quantity': sum,
                                    'excrate': move_id.customs_department,
                                    'amount_type': move_id.currency_id.name,
                                    'export_products_id': move_id.export_products_id,
                                    'company_rate': company_rate,
                                }
                                doc.append(move_ids)
                                print('doc_last:', doc)
                        elif move_id.invoice_line_ids.filtered(lambda a: a.tax_ids.id == tax.id):
                            print('move_id:',move_id.id)
                            if move_id.journal_id.type_vat == 'tax':
                                date = move_id.tax_invoice_date
                            elif move_id.journal_id.type_vat == 'not_deal':
                                date = move_id.tax_invoice_date
                            else:
                                date = move_id.tax_invoice_date

                            if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                print('aaaaa')
                                amount_untaxed = move_id.amount_untaxed
                                amount_tax = move_id.amount_tax
                                amount_total = move_id.amount_total
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                            else:
                                rate = self.env['res.currency.rate'].search(
                                    [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)], limit=1)
                                print('rate:',rate)
                                rate = rate.rate
                                amount_untaxed = move_id.amount_untaxed / rate
                                amount_tax = move_id.amount_tax / rate
                                amount_total = move_id.amount_total / rate
                                untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                            if len(move_id.invoice_line_ids) >= 2:
                                sum = 0.0
                                for i in move_id.invoice_line_ids:
                                    sum = sum + i.quantity
                                    print("ID_quantity", i, ":", i.quantity)
                            elif len(move_id.invoice_line_ids) <= 1:
                                sum = move_id.invoice_line_ids.quantity
                            if len(move_id.currency_id.rate_ids) >= 2:
                                company_rate = move_id.currency_id.rate_ids[0].company_rate
                                print("company_rate!!:", company_rate)
                            elif len(move_id.currency_id.rate_ids) < 2:
                                company_rate = move_id.currency_id.rate_ids.company_rate
                                print("company_rate!!!:", company_rate)
                            if company_rate == 0.0:
                                company_rate = 1.0
                            print("company_rate!!!!:", company_rate)
                            move_ids = {
                                'date': date.strftime("%d/%m/%Y"),
                                'name': move_id.tax_inv_number or move_id.name,
                                'partner': self.get_partner_name(move_id),
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
                                'ETD': move_id.etd,
                                'ETA': move_id.eta,
                                'quantity': sum,
                                'excrate': move_id.customs_department,
                                'amount_type': move_id.currency_id.name,
                                'export_products_id': move_id.export_products_id,
                                'company_rate': company_rate,
                            }
                            doc.append(move_ids)
                            print('doc_last:', doc)
                    else:
                        print('move_iddddd:',move_id)
                        if move_id.journal_id.type_vat == 'tax':
                            date = move_id.tax_invoice_date
                        elif move_id.journal_id.type_vat == 'not_deal':
                            date = move_id.tax_invoice_date
                        else:
                            date = move_id.tax_invoice_date

                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_untaxed = (move_id.amount_tax / 7) * 100
                            amount_tax = move_id.amount_tax
                            amount_total = amount_untaxed + amount_tax
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                limit=1)
                            rate = rate.rate
                            print('rate:', rate)
                            amount_untaxed =((move_id.amount_tax / 7) * 100) / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = (amount_untaxed + amount_tax)  / rate
                            untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                        print('move_id.amount_tax_move_id.amount_tax:',(move_id.amount_tax / 7) * 100)
                        print('move_id.amount_tax_move_id.amount_tax:',move_id.amount_tax)
                        if len(move_id.invoice_line_ids) >= 2:
                            sum = 0.0
                            for i in move_id.invoice_line_ids:
                                sum = sum + i.quantity
                                print("ID_quantity", i, ":", i.quantity)
                        elif len(move_id.invoice_line_ids) <= 1:
                            sum = move_id.invoice_line_ids.quantity
                        if len(move_id.currency_id.rate_ids) >= 2:
                            company_rate = move_id.currency_id.rate_ids[0].company_rate
                            print("company_rate!!:", company_rate)
                        elif len(move_id.currency_id.rate_ids) < 2:
                            company_rate = move_id.currency_id.rate_ids.company_rate
                            print("company_rate!!!:", company_rate)
                        if company_rate == 0.0:
                            company_rate = 1.0
                        print("company_rate!!!!:", company_rate)
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': self.get_partner_name(move_id),
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
                            'ETD': move_id.etd,
                            'ETA': move_id.eta,
                            'quantity': sum,
                            'excrate': move_id.customs_department,
                            'amount_type': move_id.currency_id.name,
                            'export_products_id': move_id.export_products_id,
                            'company_rate': company_rate,
                        }
                        doc.append(move_ids)
            else:
                print('======TAX_ID_FALSE========')
                for move_id in docs:
                    print('move_id.invoice_line_ids:',move_id.invoice_line_ids.mapped('tax_ids'))
                    all_tax_ids = len(move_id.invoice_line_ids.mapped('tax_ids'))
                    print('all_tax_ids:',all_tax_ids)
                    if all_tax_ids == 1:
                        if move_id.invoice_line_ids.filtered(lambda a: a.tax_ids and a.tax_ids.is_tax_not_due):
                            print('is_tax_not_due')
                            if move_id.adjust_move_id:
                                if move_id.journal_id.type_vat == 'tax':
                                    date = move_id.tax_invoice_date
                                elif move_id.journal_id.type_vat == 'not_deal':
                                    date = move_id.tax_invoice_date
                                else:
                                    date = move_id.tax_invoice_date
                                print('amount_type !!: ', move_id.currency_id.name)
                                if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                    amount_type = move_id.currency_id.name
                                    # print('amount_type : ', amount_type)
                                    amount_untaxed = move_id.amount_untaxed
                                    amount_tax = move_id.amount_tax
                                    amount_total = move_id.amount_total
                                    untaxed_amount_after_discount = move_id.amount_untaxed
                                    # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                                else:
                                    rate = self.env['res.currency.rate'].search([('name', '<=', move_id.invoice_date),('company_id', '=', self.env.company.id)], limit=1)
                                    # rate = rate.rate
                                    rate = 1
                                    print('rate:',rate)
                                    amount_untaxed = move_id.amount_untaxed / rate
                                    amount_tax = move_id.amount_tax / rate
                                    amount_total = move_id.amount_total / rate
                                    # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                                    untaxed_amount_after_discount = move_id.amount_untaxed / rate
                                if len(move_id.invoice_line_ids) >= 2:
                                    sum = 0.0
                                    for i in move_id.invoice_line_ids:
                                        sum = sum + i.quantity
                                        print("ID_quantity", i, ":", i.quantity)
                                elif len(move_id.invoice_line_ids) <= 1:
                                    sum = move_id.invoice_line_ids.quantity
                                if len(move_id.currency_id.rate_ids) >= 2:
                                    company_rate = move_id.currency_id.rate_ids[0].company_rate
                                    print("company_rate!!:", company_rate)
                                elif len(move_id.currency_id.rate_ids) < 2:
                                    company_rate = move_id.currency_id.rate_ids.company_rate
                                    print("company_rate!!!:", company_rate)
                                if company_rate == 0.0:
                                    company_rate = 1.0
                                print("company_rate!!!!:", company_rate)
                                move_ids = {
                                    'date': date.strftime("%d/%m/%Y"),
                                    'name': move_id.tax_inv_number or move_id.name,
                                    'partner': self.get_partner_name(move_id),
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
                                    'ETD': move_id.etd,
                                    'ETA': move_id.eta,
                                    'quantity': sum,
                                    'excrate': move_id.customs_department,
                                    'amount_type': move_id.currency_id.name,
                                    'export_products_id': move_id.export_products_id,
                                    'company_rate': company_rate,
                                }

                                doc.append(move_ids)
                        elif move_id.invoice_line_ids.filtered(lambda a: a.tax_ids):
                            print('is_tax_not_due')
                            if move_id.journal_id.type_vat == 'tax':
                                date = move_id.tax_invoice_date
                            elif move_id.journal_id.type_vat == 'not_deal':
                                date = move_id.tax_invoice_date
                            else:
                                date = move_id.tax_invoice_date
                            print('amount_type !!: ', move_id.currency_id.name)
                            if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                                amount_type = move_id.currency_id.name
                                # print('amount_type : ', amount_type)
                                amount_untaxed = move_id.amount_untaxed
                                amount_tax = move_id.amount_tax
                                amount_total = move_id.amount_total
                                # remove remove
                                # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount

                                untaxed_amount_after_discount = move_id.amount_untaxed
                                print("amount_untaxed!:", amount_untaxed)
                            else:
                                rate = self.env['res.currency.rate'].search(
                                    [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                    limit=1)
                                # rate = rate.rate
                                rate = 1
                                print('rate:', rate)
                                amount_untaxed = move_id.amount_untaxed / rate
                                amount_tax = move_id.amount_tax / rate
                                amount_total = move_id.amount_total / rate
                                print("amount_untaxed!!:", amount_untaxed)
                                print("amount_tax!!:", amount_tax)
                                print("amount_total!!:", amount_total)
                                amount_type = move_id.currency_id.name

                                # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                                untaxed_amount_after_discount = move_id.amount_untaxed / rate
                            if len(move_id.invoice_line_ids)>=2:
                                sum = 0.0
                                for i in move_id.invoice_line_ids:
                                    sum = sum + i.quantity
                                    print("ID_quantity",i,":",i.quantity)
                            elif len(move_id.invoice_line_ids) <= 1:
                                    sum = move_id.invoice_line_ids.quantity
                            if len(move_id.currency_id.rate_ids) >= 2:
                                company_rate = move_id.currency_id.rate_ids[0].company_rate
                                print("company_rate!!:", company_rate)
                            elif len(move_id.currency_id.rate_ids) < 2:
                                company_rate = move_id.currency_id.rate_ids.company_rate
                                print("company_rate!!!:", company_rate)
                            if company_rate==0.0:
                                company_rate =1.0
                            print("company_rate!!!!:",company_rate)
                            move_ids = {
                                'date': date.strftime("%d/%m/%Y"),
                                'name': move_id.tax_inv_number or move_id.name,
                                'partner': self.get_partner_name(move_id),
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
                                'ETD': move_id.etd,
                                'ETA': move_id.eta,
                                'quantity': sum,
                                'excrate': move_id.customs_department,
                                'amount_type': move_id.currency_id.name,
                                'export_products_id': move_id.export_products_id,
                                'company_rate': company_rate,
                            }
                            doc.append(move_ids)
                    else:
                        print('move_iddddd:',move_id)
                        if move_id.journal_id.type_vat == 'tax':
                            date = move_id.tax_invoice_date
                        elif move_id.journal_id.type_vat == 'not_deal':
                            date = move_id.tax_invoice_date
                        else:
                            date = move_id.tax_invoice_date

                        if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                            amount_type = move_id.currency_id.name
                            print('amount_type : ', amount_type)
                            amount_untaxed = (move_id.amount_tax / 7) * 100
                            amount_tax = move_id.amount_tax
                            amount_total = amount_untaxed + amount_tax
                            untaxed_amount_after_discount = amount_untaxed
                            # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount
                        else:
                            rate = self.env['res.currency.rate'].search(
                                [('name', '<=', move_id.invoice_date), ('company_id', '=', self.env.company.id)],
                                limit=1)
                            # rate = rate.rate
                            rate = 1
                            print('rate:', rate)
                            amount_untaxed =((move_id.amount_tax / 7) * 100) / rate
                            amount_tax = move_id.amount_tax / rate
                            amount_total = (amount_untaxed + amount_tax)  / rate
                            untaxed_amount_after_discount = amount_untaxed / rate
                            # untaxed_amount_after_discount = move_id.untaxed_amount_after_discount / rate
                        print('move_id.amount_tax_move_id.amount_tax:',(move_id.amount_tax / 7) * 100)
                        print('move_id.amount_tax_move_id.amount_tax:',move_id.amount_tax)
                        if len(move_id.invoice_line_ids) >= 2:
                            sum = 0.0
                            for i in move_id.invoice_line_ids:
                                sum = sum + i.quantity
                                print("ID_quantity", i, ":", i.quantity)
                        elif len(move_id.invoice_line_ids) <= 1:
                            sum = move_id.invoice_line_ids.quantity
                        if len(move_id.currency_id.rate_ids) >= 2:
                            company_rate = move_id.currency_id.rate_ids[0].company_rate
                            print("company_rate!!:", company_rate)
                        elif len(move_id.currency_id.rate_ids) < 2:
                            company_rate = move_id.currency_id.rate_ids.company_rate
                            print("company_rate!!!:", company_rate)
                        if company_rate == 0.0:
                            company_rate = 1.0
                        print("company_rate!!!!:", company_rate)
                        move_ids = {
                            'date': date.strftime("%d/%m/%Y"),
                            'name': move_id.tax_inv_number or move_id.name,
                            'partner': self.get_partner_name(move_id),
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
                            'ETD': move_id.etd,
                            'ETA': move_id.eta,
                            'quantity': sum,
                            'excrate': move_id.customs_department,
                            'amount_type': move_id.currency_id.name,
                            'export_products_id': move_id.export_products_id,
                            'company_rate': company_rate,
                        }
                        doc.append(move_ids)

            #  Domain For Journal Entry
            domain = [('tax_invoice_date', '>=', data['date_from']), ('tax_invoice_date', '<=', data['date_to']),
                       ('is_manual_cn','=',False),
                      ('state', 'in', ('posted', 'cancel')), ('move_type', '=', 'entry')]
            print('DOC _ INVOIE:',doc)

            docs = self.env['account.move'].search(domain)
            print('docs-c:',docs)
            for move_id in docs:
                if move_id.journal_id.type_vat == 'tax':
                    date = move_id.tax_invoice_date
                elif move_id.journal_id.type_vat == 'not_deal':
                    date = move_id.tax_invoice_date
                else:
                    date = move_id.tax_invoice_date

                for move_line in move_id.line_ids.filtered(lambda a: a.account_id.sale_tax_report == True):
                    print('amount_type !!: ', move_id.currency_id.name)
                    if move_id.currency_id.id == self.env.user.company_id.currency_id.id:
                        print('aaaaa')
                        amount_type = move_id.currency_id.name
                        # print('amount_type : ', amount_type)
                        amount_untaxed = move_line.tax_base_amount
                        amount_tax = move_line.credit
                        amount_total = move_line.tax_base_amount + move_line.credit

                    else:
                        rate = self.env['res.currency.rate'].search(
                            [('name', '<=', move_id.tax_invoice_date), ('company_id', '=', self.env.company.id)], limit=1)
                        print('rate:',rate)
                        # rate = rate.rate
                        rate = 1
                        amount_untaxed = move_line.tax_base_amount / rate
                        amount_tax =  move_line.credit / rate
                        amount_total = (move_line.tax_base_amount + move_line.credit) / rate
                    if len(move_id.invoice_line_ids) >= 2:
                        sum = 0.0
                        for i in move_id.invoice_line_ids:
                            sum = sum + i.quantity
                            print("ID_quantity", i, ":", i.quantity)
                    elif len(move_id.invoice_line_ids) <= 1:
                        sum = move_id.invoice_line_ids.quantity
                    if len(move_id.currency_id.rate_ids) >= 2:
                        company_rate = move_id.currency_id.rate_ids[0].company_rate
                        print("company_rate!!:", company_rate)
                    elif len(move_id.currency_id.rate_ids) < 2:
                        company_rate = move_id.currency_id.rate_ids.company_rate
                        print("company_rate!!!:", company_rate)
                    if company_rate == 0.0:
                        company_rate = 1.0
                    print("company_rate!!!!:", company_rate)
                    move_ids = {
                        'date': date.strftime("%d/%m/%Y"),
                        'name': move_id.tax_inv_number or move_id.name,
                        'partner': self.get_partner_name(move_id),
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
                        'ETD': move_id.etd,
                        'ETA': move_id.eta,
                        'quantity': sum,
                        'excrate': move_id.customs_department,
                        'amount_type': move_id.currency_id.name,
                        'export_products_id': move_id.export_products_id,
                        'company_rate': company_rate,
                    }
                    doc.append(move_ids)
            doc.sort(key=lambda k: (k['date'], k['name']))
            return {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'docs': doc,
                'company_id': company_id,
                'data': data,
            }


#start This is to generate purchase tax report
class report_purchase_tax_report(models.AbstractModel):
    _name = 'report.itaas_print_tax_report.purchase_tax_report_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values_purchase:')
        print('data:',data)
        company_id = self.env.company
        move_line_ids = {}
        doc = []
        # print('===================================CASE#1==========================================')
        if 'operating_unit' in data and data['operating_unit']:
            print('operating_unit Purchase')
            domain = [('account_id.purchase_tax_report', '=', True), ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', '=', 'posted'), ('date_maturity', '=', False),
                      ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry'))
                      # ('exclude_from_invoice_tab', '=', True)
                ,('is_special_tax', '=', False),
                      ('operating_unit_id', 'in', data['operating_unit'])]
            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                print('account_ids:',account_ids)
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids and x.debit == 0 and x.credit == 0):
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref
                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))

                    if move_line_id.move_id.move_type == 'in_refund':
                        if move_line_id.tax_base_amount:
                            amount_untaxed = move_line_id.tax_base_amount * (-1)
                        elif move_line_id.amount_before_tax:
                            amount_untaxed = move_line_id.amount_before_tax * (-1)
                        else:
                            amount_untaxed = abs(move_line_id.balance) * (100/7) * (-1)

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
                            amount_untaxed = abs(move_line_id.balance) * (100/7)

                        if move_line_id.debit:
                            amount_tax = move_line_id.debit
                        else:
                            amount_tax = move_line_id.credit
                    amount_total = amount_untaxed + amount_tax
                    move_line_ids = {
                        'date': date_t2,
                        'ref': ref,
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
                        'operating_unit_id':move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            else:
                print('vat All case 1 ou')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs:', docs)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids):
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']))
        else:
            print('not operating_unit')
            domain = [('account_id.purchase_tax_report', '=', True),('tax_inv_date','>=',data['date_from']),
                      ('tax_inv_date','<=',data['date_to']),
                      ('move_id.state','in',('posted','cancel')),('date_maturity','=',False),
                      ('move_id.move_type','in',('in_invoice','in_refund','entry')),
                      # ('exclude_from_invoice_tab','=',True),
                      ('is_special_tax', '=', False)]

            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids and x.debit == 0 and x.credit == 0):
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                    else:
                        date_t2 = move_line_id.tax_inv_date
                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref
                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
            else:
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax[0].invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs:',docs)
                print('account_ids:',account_ids)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids):
                    print('move_line_id:',move_line_id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                    else:
                        date_t2 = move_line_id.tax_inv_date
                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
                        'state':move_line_id.move_id.state,
                    }
                    doc.append(move_line_ids)
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        # print('===================================CASE#2==========================================')
        if 'operating_unit' in data and data['operating_unit']:
            domain = [('account_id.purchase_tax_report', '=', True), ('date_maturity', '>=', data['date_from']),
                      ('date_maturity', '<=', data['date_to']),('move_id.state', '=', 'posted'),
                      ('date_maturity', '!=', False),
                      # ('exclude_from_invoice_tab','=',True),
                      ('is_special_tax', '=', False),
                      ('operating_unit_id', 'in', data['operating_unit'])]
            print('domain2:', domain)
            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                print('account_ids:', account_ids)
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(
                        lambda x: x.account_id in account_ids and x.debit == 0 and x.credit == 0):
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref
                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))

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
                        'ref': ref,
                        'partner': move_line_id.partner_id,

                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'debit': move_line_id.debit,
                        'credit': move_line_id.credit,
                        'note': move_line_id.move_id.name,
                        'type': move_line_id.move_id.move_type,
                        'move_id': move_line_id.move_id,
                        'state': move_line_id.move_id.state,
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            else:
                print('vat All Case 2 ou')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs:', docs)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids):
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('move_line_id.type:', move_line_id.move_id.move_type)
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
                        'ref': ref,
                        'partner': move_line_id.partner_id,

                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'debit': move_line_id.debit,
                        'credit': move_line_id.credit,
                        'note': move_line_id.move_id.name,
                        'type': move_line_id.move_id.move_type,
                        'move_id': move_line_id.move_id,
                        'state': move_line_id.move_id.state,
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        else:
            domain = [('account_id.purchase_tax_report', '=', True), ('date_maturity', '>=', data['date_from']),
                      ('date_maturity', '<=', data['date_to']), ('move_id.state', '=', 'posted'),
                      ('date_maturity', '!=', False),
                      # ('exclude_from_invoice_tab', '=', True),
                      ('is_special_tax', '=', False)]
            print('domain2:', domain)
            if 'vat_0' in data and data['vat_0']:

                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids and x.debit == 0 and x.credit == 0):
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                    else:
                        date_t2 = move_line_id.tax_inv_date

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
            else:
                print('vat All Case 2 NOT ou')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(lambda x: x.account_id in account_ids):
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('move_line_id.type:', move_line_id.move_id.move_type)
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
                        'ref': ref,
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
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        # print('=====================================CASE#3========================================')
        if 'operating_unit' in data and data['operating_unit']:
            print('case 3 OU')
            domain = [('account_id.purchase_tax_report', '=', False), ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', 'in', ('posted','cancel')), ('date_maturity', '=', False),
                      ('tax_line_id.type_tax_use','=','purchase'),
                      ('operating_unit_id', 'in', data['operating_unit']),
                      # ('exclude_from_invoice_tab', '=', True),
                      ('is_special_tax', '=', True)]
            print('docs_3:', docs)
            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                print('account_ids:', account_ids)
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs:
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref
                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))

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
                        'ref': ref,
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
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            else:
                print('vat All Case 3 NOT OU')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs:', docs)
                for move_line_id in docs:
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('move_line_id.type:', move_line_id.move_id.move_type)
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
                        'ref': ref,
                        'partner': move_line_id.partner_id,

                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'debit': move_line_id.debit,
                        'credit': move_line_id.credit,
                        'note': move_line_id.move_id.name,
                        'type': move_line_id.move_id.move_type,
                        'move_id': move_line_id.move_id,
                        'state': move_line_id.move_id.state,
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        else:
            print('case3 not ou')
            domain = [('account_id.purchase_tax_report', '=', False), ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', 'in', ('posted','cancel')), ('date_maturity', '=', False),
                      ('tax_line_id.type_tax_use','=','purchase'),
                      # ('exclude_from_invoice_tab', '=', True),
                      ('is_special_tax', '=', True)]

            if 'vat_0' in data and data['vat_0']:

                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs.filtered(lambda x: x.tax_line_id.amount == 0):
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
            else:
                print('vat All Case 3')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('is_special_tax:',docs)

                for move_line_id in docs:
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
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
                        'ref': ref,
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
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)

        # print('=====================================CASE#4 ========================================')
        if 'operating_unit' in data and data['operating_unit']:
            print('case 4 OU')
            domain = [('account_id.purchase_tax_report', '=', True), ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', 'in', ('posted', 'cancel')), ('date_maturity', '!=', False),
                      # ('exclude_from_invoice_tab', '=', True), 
                      ('is_special_tax', '=', True),
                      ('operating_unit_id', 'in', data['operating_unit'])]
            print('docs_4:', docs)
            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                print('account_ids:', account_ids)
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs:
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref
                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))

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
                        'ref': ref,
                        'partner': move_line_id.partner_id,
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'debit': move_line_id.debit,
                        'credit': move_line_id.credit,
                        'note': move_line_id.move_id.name,
                        'type': move_line_id.move_id.move_type,
                        'move_id': move_line_id.move_id,
                        'state': move_line_id.move_id.state,
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            else:
                print('vat All Case 4 NOT OU')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs:', docs)
                for move_line_id in docs:
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('move_line_id.type:', move_line_id.move_id.move_type)
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
                        'ref': ref,
                        'partner': move_line_id.partner_id,

                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_total,
                        'debit': move_line_id.debit,
                        'credit': move_line_id.credit,
                        'note': move_line_id.move_id.name,
                        'type': move_line_id.move_id.move_type,
                        'move_id': move_line_id.move_id,
                        'state': move_line_id.move_id.state,
                        'operating_unit_id': move_line_id.operating_unit_id,

                    }
                    doc.append(move_line_ids)
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        else:
            print('case4 not ou')
            domain = [('account_id.purchase_tax_report', '=', True), ('tax_inv_date', '>=', data['date_from']),
                      ('tax_inv_date', '<=', data['date_to']),
                      ('move_id.state', 'in', ('posted', 'cancel')), ('date_maturity', '!=', False),
                      # ('exclude_from_invoice_tab', '=', True),
                      ('is_special_tax', '=', True)]

            if 'vat_0' in data and data['vat_0']:
                print('Vat 0')
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('amount', '=', 0),
                                                      ('type_tax_use', '=', 'purchase')])
                print('tax:', tax)
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                print('docs_specail:', docs)
                for move_line_id in docs.filtered(lambda x: x.tax_line_id.amount == 0):
                    print('move_line_id:', move_line_id.id)
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('move_line_id.type:', move_line_id.move_id.move_type)
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
                        'ref': ref,
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
            else:
                tax = self.env['account.tax'].search([('tax_report', '=', True),
                                                      ('type_tax_use', '=', 'purchase')])
                account_ids = tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id).mapped('account_id')
                docs = self.env['account.move.line'].search(domain)
                for move_line_id in docs:
                    if move_line_id.date_vat_new:
                        date_t2 = move_line_id.date_vat_new
                        # date_t2 = move_line_id.date_vat_new.strftime("%d/%m/%Y")
                    else:
                        date_t2 = move_line_id.tax_inv_date
                        # date_t2 = move_line_id.tax_inv_date.strftime("%d/%m/%Y")

                    if not date_t2:
                        raise UserError(_("Please check date for item %s" % move_line_id.move_id.name))
                    if move_line_id.ref_new:
                        ref = move_line_id.ref_new
                    else:
                        ref = move_line_id.ref

                    if not ref:
                        raise UserError(_("Please check ref for item %s" % move_line_id.move_id.name))
                    if move_line_id.move_id.move_type == 'in_refund':
                        print('move_line_id.move_id:', move_line_id.move_id)
                        print('refunddddddddddddddddddddddddddd')
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
                        'ref': ref,
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
            if doc:
                doc.sort(key=lambda k: (k['date'], k['ref']), reverse=False)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': doc,
            'company_id': company_id,
            'data': data,
        }
