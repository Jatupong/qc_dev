# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    adjust_move_count = fields.Integer('Count Adjust',compute='_get_invoiced_count_adjust_line')

    originnal_reverse = fields.Many2many('account.move',string="Originnal Reverse")

    tax_return_amount = fields.Float('ยอดกลับรายการภาษี',related="move_id.amount_for_reverse")



    def _get_invoiced_count_adjust_line(self):
        for obj in self:
            move_ids = len(self.env['account.move'].search([('ref','=',obj.move_id.name),
                                                            ('move_type','=','entry'),
                                                           ('journal_id.is_reverse_journal', '=', True)
                                                            ]))
            obj.adjust_move_count = move_ids



class AccountMove(models.Model):
    _inherit = "account.move"

    adjust_require = fields.Boolean(string="Tax Adjust Require", default=False)
    is_debit_note = fields.Boolean(string='Is Debit Note')
    adjust_move_count = fields.Integer('Count Adjust',compute='_get_invoiced_count_adjust')


    def _get_invoiced_count_adjust(self):
        for obj in self:
            move_ids = len(self.env['account.move'].search([('ref','=',obj.name),
                                                            ('move_type','=','entry'),
                                                            ('journal_id.is_reverse_journal','=',True)]))
            obj.adjust_move_count = move_ids



    def action_view_invoice_adjust(self):
        invoices = self.env['account.move'].search([('ref','=',self.name),('move_type','=','entry'),('journal_id.is_reverse_journal','=',True)])
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

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
                print('purchaseeeeeeeeeee')
                print('line:',line)
                if not line.account_id.purchase_tax_report:
                    print('xxxxxxxxxx')
                    tax_account_id = self.env['account.account'].search([('purchase_tax_report', '=', True)], limit=1)
                    print('tax_account_id:',tax_account_id)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    print('aaaaaa')
                    continue
            print('=============xxx')
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
        tax_inv_number = self._context.get('tax_inv_number')
        reverse_date = self._context.get('tax_invoice_date')
        print('action_invoice_generate_tax_invoice',tax_inv_number)
        print('action_invoice_generate_tax_invoice',reverse_date)
        print('self:',self)
        if self.move_type in ('out_invoice','out_refund'):
            print('test:',self.invoice_line_ids.filtered(lambda r:r.account_id.sale_tax_report == False and not r.tax_ids.tax_report))
            tax = self.invoice_line_ids.filtered(lambda r: r.tax_ids).mapped('tax_ids')
            account = tax.invoice_repartition_line_ids.filtered(lambda r: r.account_id and r.account_id.sale_tax_report == False)
            tax_report = tax.filtered(lambda r: r.tax_report == False)
            if account and tax_report:
                if not self.tax_inv_number and self.journal_id.tax_invoice_sequence_id:
                    if not self.tax_invoice_date and reverse_date:
                        self.tax_invoice_date = reverse_date
                    else:
                        self.tax_invoice_date = fields.Date.today()
                    sequence = self.journal_id.tax_invoice_sequence_id
                    name_seq = sequence.with_context(ir_sequence_date=self.tax_invoice_date).next_by_id() or '/'
                    self.tax_inv_number = name_seq
                    self.tax_inv_generated = True
                    return self.create_reverse_tax(self.tax_inv_number,self.tax_invoice_date)
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
                    raise UserError(_("Please setup tax invoice/receipt sequence number"))
            else:
                if not self.tax_inv_number and self.journal_id.tax_invoice_sequence_id:
                    if not self.tax_invoice_date:
                        self.tax_invoice_date = fields.Date.today()
                    sequence = self.journal_id.tax_invoice_sequence_id
                    name_seq = sequence.with_context(ir_sequence_date=self.tax_invoice_date).next_by_id() or '/'
                    self.tax_inv_number = name_seq
                    self.tax_inv_generated = True

                elif not self.tax_inv_number and not self.journal_id.tax_invoice_sequence_id:
                    raise UserError(_("Please setup tax invoice/receipt sequence number"))


        else:
            print('This is purchase side')
            ######### This is purchase side########
            if self.adjust_move_id:
                return
            return self.create_reverse_tax(tax_inv_number,reverse_date)

    def create_reverse_tax(self,tax_inv_number,reverse_date):
        print('create_reverse_tax',tax_inv_number)
        print('reverse_date',reverse_date)
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
                print('purchaseeeeeeeeeeeeeeeee')
                # line.is_special_tax = True
                if not line.account_id.purchase_tax_report:
                    tax_account_id = self.env['account.account'].search([('purchase_tax_report', '=', True)], limit=1)
                    if not self.journal_id.adj_journal:
                        raise UserError(_("Please setup journal to reverse tax on invoice journal"))
                else:
                    continue
            print('==========CC_STATT')
            tax = self.invoice_line_ids.filtered(lambda r:r.tax_ids).mapped('tax_ids')
            account = tax.invoice_repartition_line_ids.filtered(lambda r:r.account_id and r.account_id.purchase_tax_report == False)
            tax_report = tax.filtered(lambda r:r.tax_report == False)
            new_ref = tax_inv_number
            print('account:',account)
            print('tax_report:',tax_report)
            if account and tax_report:
                original_tax_line = {
                    'name': line.name,
                    'amount_currency': -line.amount_currency if line.currency_id else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'debit': line.credit,
                    'credit': line.debit,
                    'amount_before_tax' : line.tax_base_amount,
                    'ref': self.name,
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'payment_id': False,
                }
                new_tax_line = {
                    'name': tax_account_id.name,
                    'amount_currency': line.amount_currency if line.currency_id else 0.0,
                    'currency_id': line.currency_id.id or False,
                    'debit': line.debit,
                    'credit': line.credit,
                    'amount_before_tax': line.tax_base_amount,
                    'ref': self.tax_inv_number,
                    'date_maturity': self.tax_invoice_date,
                    'partner_id': line.partner_id.id,
                    'account_id': tax_account_id.id,
                    'payment_id': False,
                    # 'exclude_from_invoice_tab': False,
                    'is_special_tax': True,
                }
                print('original_tax_line',original_tax_line)
                print ('new_tax_line',new_tax_line)
                line_ids.append((0, 0, original_tax_line))
                line_ids.append((0, 0, new_tax_line))

                if line_ids:
                    print ('LINEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
                    print (line_ids)
                    # date = self._context.get('date')
                    date = reverse_date or self._context.get('date')

                    print('xxx:',date)
                    move_vals = {
                        'move_type': 'entry',
                        'date': date or self.tax_invoice_date or fields.datetime.today(),
                        'ref': self.name,
                        'tax_invoice_date': date or self.tax_invoice_date or fields.datetime.today(),
                        'journal_id': self.journal_id.adj_journal.id,
                        'currency_id': self.currency_id.id or self.journal_id.currency_id.id or self.company_id.currency_id.id,
                        'partner_id': self.partner_id.id,
                        'line_ids': line_ids
                    }
                    print('move_vals_move_vals:',move_vals)
                    move_id = self.env['account.move'].create(move_vals)
                    print('move_id_move_id:',move_id)
                    invoices = self.env['account.move'].search(
                        [('ref', '=', line.move_id.name), ('move_type', '=', 'entry'),
                         ('journal_id.is_reverse_journal', '=', True)])
                    invoices |= move_id

                    line.originnal_reverse = [(6, 0, invoices.ids)]
                    move_id.action_post()
                    new_tax_line = move_id.line_ids.filtered(lambda x: x.account_id == tax_account_id)
                    print('New Tax Line', new_tax_line)
                    new_tax_line.update({'ref': new_ref})
                    self.adjust_move_id = move_id
                    self.amount_for_reverse = self.amount_tax
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



