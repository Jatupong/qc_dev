# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    adjust_require = fields.Boolean(string="Tax Adjust Require", default=False)

    def _get_sequence(self):
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''

        self.ensure_one()
        journal = self.journal_id
        # res = super(AccountMove, self)._get_sequence()
        if self.move_type in ('out_invoice', 'in_invoice','out_refund','in_refund') and self.is_debit_note and journal.debit_sequence_id:
            sequence = journal.debit_sequence_id
            name_seq = sequence.with_context(ir_sequence_date=self.invoice_date).next_by_id() or '/'

            # self.name = name_seq
            return name_seq
        return

    def action_post(self):
        print('Test action:')
        if self.name == '/' and self.move_type != 'entry':
            if self.invoice_date:
                sequence = self._get_sequence()
                print('test sequence:',sequence)
                # name_seq = sequence.with_context(ir_sequence_date=self.invoice_date).next_by_id() or '/'
                self.name = sequence
            else:
                self.invoice_date = fields.Date.today()
        return super(AccountMove, self).action_post()
        # for obj in self:
        #     if obj.move_type in ('in_invoice','in_refund'):
        #         if not obj.ref:
        #             raise UserError(_('Please Set Reference !'))
        #
        # return super(AccountMove, self).action_post()



    # def action_post(self):
    #     print('postttttttttttttttttttttt')
    #     if self.move_type in ('in_invoice', 'in_refund'):
    #         if not self.ref:
    #             raise UserError(_('Please Set Reference !'))
    #     for obj in self:
    #         if obj.move_type in ('in_invoice', 'in_refund'):
    #             if not obj.ref:
    #                 raise UserError(_('Please Set Reference !'))
    #         if self.name == '/' and self.move_type != 'entry':
    #             if self.invoice_date:
    #                 sequence = self._get_sequence()
    #                 name_seq = sequence.with_context(ir_sequence_date=self.invoice_date).next_by_id() or '/'
    #                 self.name = name_seq
    #             else:
    #                 self.invoice_date = fields.Date.today()
    #     return super(AccountMove, self).action_post()


    def create_reverse_tax_partial(self,amount,tax_amount,tax_inv_number,date_result):
        print('create_reverse_taxxxxxxxxxxxxxxxxxxx')
        print('amount:',amount)
        print('tax_amount:',tax_amount)
        print('tax_inv_number:',tax_inv_number)
        print('date_result:',date_result)
        line_ids = []
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            if self.move_type in ('out_invoice', 'out_refund'):
                if not line.account_id.sale_tax_report:
                    tax_account_id = self.env['account.account'].search([('sale_tax_report','=',True)],limit=1)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    continue
            else:
                print('purchase')
                print('line:',line)
                if not line.account_id.purchase_tax_report:
                    tax_account_id = self.env['account.account'].search([('purchase_tax_report', '=', True)], limit=1)
                    print('tax_account_id:',tax_account_id)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    continue
            print('aaa')
            tax = self.invoice_line_ids.filtered(lambda r:r.tax_ids).mapped('tax_ids')
            print('tax',tax)
            account = tax.invoice_repartition_line_ids.filtered(lambda r:r.account_id and r.account_id.purchase_tax_report == False)
            tax_report = tax.filtered(lambda r:r.tax_report == False)
            print('account:',account)
            print('tax_report:',tax_report)
            if account and tax_report:
                print('bbbbbbbbbbbbbbbbbbbbb')
                print('line.name:',line.name)
                print(':tax_account_id.name',tax_account_id.name)
                original_tax_line = {
                    'name': line.name,
                    'amount_currency': -tax_amount if tax_amount else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'amount_before_tax': amount,
                    # 'ref': line.ref,
                    'debit': 0.00,
                    'credit': tax_amount,
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,

                    'payment_id': False,
                }
                new_tax_line = {
                    'name': tax_account_id.name,
                    'amount_currency': tax_amount if tax_amount else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'amount_before_tax': amount,
                    # 'ref':new_ref,
                    'debit': tax_amount,
                    'credit': 0.00,
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': tax_account_id.id,
                    'is_special_tax': True,
                    # 'exclude_from_invoice_tab': True,
                    'payment_id': False,
                }
                print('================: original_tax_line',original_tax_line)
                print('================: new_tax_line',new_tax_line)
                line_ids.append((0, 0, original_tax_line))
                line_ids.append((0, 0, new_tax_line))

                if line_ids:
                    print ('LINE')
                    print (line_ids)
                    date = self._context.get('date')

                    print('xxx:',date)
                    move_vals = {
                        'move_type': 'entry',
                        'date': date or self.tax_invoice_date or fields.datetime.today(),
                        'ref': self.name,
                        'tax_invoice_date': date_result,
                        'journal_id': self.journal_id.adj_journal.id,
                        'currency_id': self.currency_id.id or self.journal_id.currency_id.id or self.company_id.currency_id.id,
                        'partner_id': self.partner_id.id,
                        'line_ids': line_ids
                    }
                    print('**** move_vals:',move_vals)
                    move_id = self.env['account.move'].create(move_vals)
                    invoices = self.env['account.move'].search(
                        [('ref', '=', line.move_id.name), ('move_type', '=', 'entry'),
                         ('journal_id.is_reverse_journal', '=', True)])
                    invoices |= move_id

                    line.originnal_reverse = [(6,0,invoices.ids)]

                    print('move_id____LAST:',move_id)
                    if self.move_type in ('in_invoice', 'in_refund'):
                        new_tax_line = move_id.line_ids.filtered(lambda x: x.account_id == tax_account_id)
                        print ('New Tax Line',new_tax_line)
                        new_tax_line.update({'ref': tax_inv_number})
                    self.adjust_move_id = move_id
                    move_id.action_post()
                    # self.write({'adjust_move_multi_ids': [(4, [move_id.id])]})
                    return move_id


    def action_invoice_generate_tax_invoice(self):
        print('action_invoice_generate_tax_invoice')
        if self.move_type in ('out_invoice','out_refund'):
            print('test:',self.invoice_line_ids.filtered(lambda r:r.account_id.sale_tax_report == False and not r.tax_ids.tax_report))
            tax = self.invoice_line_ids.filtered(lambda r: r.tax_ids).mapped('tax_ids')
            account = tax.invoice_repartition_line_ids.filtered(lambda r: r.account_id and r.account_id.sale_tax_report == False)
            tax_report = tax.filtered(lambda r: r.tax_report == False)
            if account and tax_report:
                if not self.tax_inv_number and self.journal_id.tax_invoice_sequence_id:
                    if not self.tax_invoice_date:
                        self.tax_invoice_date = fields.Date.today()
                    sequence = self.journal_id.tax_invoice_sequence_id
                    name_seq = sequence.with_context(ir_sequence_date=self.tax_invoice_date).next_by_id() or '/'
                    self.tax_inv_number = name_seq
                    self.tax_inv_generated = True
                    print('==========xxxxxxxxxxxxxx')
                    return self.create_reverse_tax()
                #remove by JA - 19/06/2021 - ne need receipt sequence
                # elif not self.tax_inv_number and not self.journal_id.tax_invoice_sequence_id and self.journal_id.sequence_receipt:
                #     print('======================')
                #     if not self.receipt_date:
                #         print('xxxxxxxxxxxx')
                #         self.receipt_date = fields.Date.today()
                #     sequence = self.journal_id.sequence_receipt
                #     name_seq = sequence.with_context(ir_sequence_date=self.receipt_date).next_by_id() or '/'
                #     self.tax_inv_number = name_seq
                #     self.tax_inv_generated = True
                #     self.create_reverse_tax()

                elif not self.tax_inv_number and not self.journal_id.tax_invoice_sequence_id:
                    print('tttttttt')
                    raise UserError(_("Please setup tax invoice/receipt sequence number"))
            else:
                print('aaaaaaa')
                if not self.tax_inv_number and self.journal_id.tax_invoice_sequence_id:
                    print('CCASE1')
                    if not self.tax_invoice_date:
                        print('CCASE1_1')
                        self.tax_invoice_date = fields.Date.today()
                    print('CCASE2')
                    sequence = self.journal_id.tax_invoice_sequence_id
                    print('CCASE3')
                    name_seq = sequence.with_context(ir_sequence_date=self.tax_invoice_date).next_by_id() or '/'
                    self.tax_inv_number = name_seq
                    self.tax_inv_generated = True

                elif not self.tax_inv_number and not self.journal_id.tax_invoice_sequence_id:
                    print('gggggggg')
                    raise UserError(_("Please setup tax invoice/receipt sequence number"))


        else:
            print('This is purchase side')
            ######### This is purchase side########
            return self.create_reverse_tax()

    def create_reverse_tax(self):
        print('create_reverse_tax')
        line_ids = []
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            print('lineeeeeeeeeeeeeeeee:',line)
            if self.move_type in ('out_invoice', 'out_refund'):
                print('CASE1')
                if not line.account_id.sale_tax_report:
                    print('CASE2')
                    tax_account_id = self.env['account.account'].search([('sale_tax_report','=',True)],limit=1)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    continue
            else:
                print('purchase')
                line.is_special_tax = True
                if not line.account_id.purchase_tax_report:
                    tax_account_id = self.env['account.account'].search([('purchase_tax_report', '=', True)], limit=1)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    continue
            tax = self.invoice_line_ids.filtered(lambda r:r.tax_ids).mapped('tax_ids')
            account = tax.invoice_repartition_line_ids.filtered(lambda r:r.account_id and r.account_id.purchase_tax_report == False)
            tax_report = tax.filtered(lambda r:r.tax_report == False)
            if account and tax_report:
                print('bbbbbbbbbbbbbbbbbbbbb')
                print('currency_id:',line.currency_id.name)
                original_tax_line = {
                    'name': line.name,
                    'amount_currency': abs(line.amount_currency) if line.currency_id else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'debit': abs(line.credit),
                    'credit': 0.00,
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'payment_id': False,
                }


                new_tax_line = {
                    'name': tax_account_id.name,
                    'amount_currency': line.amount_currency if line.currency_id else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'debit': 0.00,
                    'credit': abs(line.credit),
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': tax_account_id.id,
                    'payment_id': False,
                }
                line_ids.append((0, 0, original_tax_line))
                line_ids.append((0, 0, new_tax_line))
                print('new_tax_line:',new_tax_line)
                print('original_tax_lin e:',original_tax_line)
                if line_ids:
                    print ('LINE')
                    print (line_ids)
                    date = self._context.get('date')

                    print('xxx:',date)
                    move_vals = {
                        'move_type': 'entry',
                        'date': date or self.tax_invoice_date or fields.datetime.today(),
                        'tax_invoice_date': self.tax_invoice_date,
                        'ref': self.name,
                        'journal_id': self.journal_id.adj_journal.id,
                        'currency_id': self.currency_id.id or self.journal_id.currency_id.id or self.company_id.currency_id.id,
                        'partner_id': self.partner_id.id,
                        'line_ids': line_ids
                    }
                    print('CREATE_',move_vals)
                    # for i in line_ids:
                    #     print('iiiiiiiii:',i)
                    move_id = self.env['account.move'].create(move_vals)
                    print('aafter_create_move_id:',move_id)
                    move_id.action_post()
                    self.adjust_move_id = move_id
                    print('move_id_END:',move_id)
                    return move_id

    def get_reverse_tax_line(self):
        for move in self:
            line_ids = move.line_ids.filtered(lambda r: r.payment_id)
            if line_ids and line_ids[0].payment_id:
                return self.env['account.move.line'].search([('payment_id','=',line_ids[0].payment_id.id),('move_id','!=',move.id)])
            else:
                return False


    @api.onchange("invoice_date")
    def onchange_invoice_date(self):
        for obj in self:
            if obj.invoice_date:
                obj.tax_invoice_date = obj.invoice_date



