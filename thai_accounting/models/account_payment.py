# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp
from datetime import datetime, date

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

# class refund_record_ids(models.Model):
#     _name = 'payment.refund.record'
#
#     invoice_id = fields.Many2one('account.move', string='Invoice')
#     amount = fields.Float(string='Payment Amount')
#     date = fields.Date(string='Date')
#     payment_id = fields.Many2one('account.payment', string='Payment')

class account_payment(models.Model):
    _inherit = "account.payment"

    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts.line', 'payment_id', string='Write Off Accounts')
    bank_cheque = fields.Boolean(string='Is Cheque', related='journal_id.bank_cheque',store=True)
    cheque_bank = fields.Many2one('res.bank', string="Bank")
    cheque_branch = fields.Char(string="Branch")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    remark = fields.Char(string="Payment Remark")
    cheque_reg_id = fields.Many2one('account.cheque.statement', string='Cheque Record')

    #GEN SEQUENCE PAYMENT AND JOURNAL >> EDIT FROM ADDONS
    # @api.depends('journal_id', 'payment_method_code')
    # def _compute_check_number(self):
    #     print('_compute_check_number_AAAAA:')
    #     for pay in self:
    #         if pay.journal_id.check_manual_sequencing and pay.payment_method_code == 'check_printing':
    #             if pay.reconciled_invoice_ids:
    #                 sequence = pay.reconciled_invoice_ids.mapped('journal_id').payment_sequence_id
    #             else:
    #                 sequence = pay.reconciled_bill_ids.mapped('journal_id').payment_sequence_id
    #             if sequence:
    #                 pay.check_number = sequence.with_context(ir_sequence_date=pay.date).next_by_id() or '/'
    #         else:
    #             if pay.reconciled_invoice_ids:
    #                 sequence = pay.reconciled_invoice_ids.mapped('journal_id').payment_sequence_id
    #             else:
    #                 sequence = pay.reconciled_bill_ids.mapped('journal_id').payment_sequence_id
    #             if sequence:
    #                 pay.name = sequence.with_context(ir_sequence_date=pay.date).next_by_id() or '/'

    def action_post(self):
        print('Case 1 action_post')
        res = super(account_payment, self).action_post()
        for payment in self:
            if payment.bank_cheque and not payment.cheque_reg_id:
                if payment.partner_type == 'customer':
                    type = 'rec'
                else:
                    type = 'pay'
                vals_cheque_rec = {
                    'issue_date': payment.date,
                    'ref': payment.ref,
                    'cheque_bank': payment.cheque_bank.id,
                    'partner_id': payment.partner_id.id,
                    'cheque_branch': payment.cheque_branch,
                    'cheque_number': payment.cheque_number,
                    'cheque_date': payment.cheque_date,
                    'amount': payment.amount,
                    'journal_id': payment.journal_id.id,
                    'user_id': self.env.user.id,
                    'communication': payment.remark,
                    'company_id': payment.env.user.company_id.id,
                    'type': type,
                    'payment_id': payment.id,
                }
                self.cheque_reg_id = self.env['account.cheque.statement'].create(vals_cheque_rec).id
                if self.move_id:
                    self.cheque_reg_id.move_id = self.move_id.id
        return res

    #UPDATE WHT
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        print('_prepare_move_line_default_vals', write_off_line_vals)
        res = super(account_payment, self)._prepare_move_line_default_vals(write_off_line_vals)
        print('_prepare_move_line_default_valsssssssssssssssssssss:', res)
        if write_off_line_vals:
            print('STep-91', write_off_line_vals)
            for write_off_line_val in write_off_line_vals:
                for write_off_line in res:
                    print('STep-92')
                    account_id = self.env['account.account'].browse(write_off_line['account_id'])
                    print('STep-93', account_id.name)
                    print('STep-93', account_id.wht)
                    if account_id.wht == True:
                        print('STep-94')
                        write_off_line['wht_type'] = write_off_line_val['wht_type']
                        write_off_line['wht_tax'] = write_off_line_val['wht_tax']
                        write_off_line['amount_before_tax'] = write_off_line_val['amount_before_tax']
                        write_off_line['date_maturity'] = write_off_line_val['date_maturity']
                return res
        else:
            # if no write_off_line_vals
            # we normally don't use standard write off val and may have our own write off
            # but if difference currency we will not support
            if self.currency_id != self.env.user.company_id.currency_id:
                print('jjjjjj')
                return res

            # if same currency then we can support multi-write off
            else:
                print('ELSEEEEEE')
                print('self._context:', self._context)
                try:
                    new_data_temp = []
                    if self.payment_type == 'inbound':
                        print('inbound')
                        credit_line_ids = list(filter(lambda m: m['credit'], res))
                        debit_line_ids = list(filter(lambda m: m['debit'], res))
                        print('credit_line_ids:', credit_line_ids)
                        print('debit_line_ids:', debit_line_ids)
                        print('==== START')
                        amount_payment = self.amount
                        credit_amount = credit_line_ids[0]['credit']
                        debit_amount = debit_line_ids[0]['debit']
                        for writeoff_multi_acc_new_id in self.writeoff_multi_acc_ids:
                            if writeoff_multi_acc_new_id.amount > 0:
                                amount_payment += abs(writeoff_multi_acc_new_id.amount)
                            else:
                                amount_payment -= abs(writeoff_multi_acc_new_id.amount)
                        print('credit_amount:', credit_amount)
                        print('debit_amount:', debit_amount)
                        print('amount_payment:', amount_payment)
                        for debit_line_id in debit_line_ids:
                            print('DEBIT;', debit_line_id['debit'])
                            vals_new = {
                                'name': debit_line_id['name'],
                                'date_maturity': debit_line_id['date_maturity'],
                                'amount_currency': debit_line_id['debit'],
                                'currency_id': debit_line_id['currency_id'],
                                'debit': debit_line_id['debit'],
                                'credit': 0.00,
                                'partner_id': debit_line_id['partner_id'],
                                'account_id': debit_line_id['account_id'],
                            }
                            new_data_temp.append(vals_new)
                        for writeoff_multi_acc_new_id in self.writeoff_multi_acc_ids:
                            print('writeoff_multi_acc_new_id.amount:', writeoff_multi_acc_new_id.amount)
                            if writeoff_multi_acc_new_id.amount > 0:
                                vals_new = {
                                    'name': writeoff_multi_acc_new_id.name,
                                    'date_maturity': self.date,
                                    'amount_currency': abs(writeoff_multi_acc_new_id.amount),
                                    'currency_id': self.currency_id.id,
                                    'debit': abs(writeoff_multi_acc_new_id.amount),
                                    'credit': 0.00,
                                    'partner_id': self.partner_id.id,
                                    'account_id': writeoff_multi_acc_new_id.writeoff_account_id.id,
                                }
                            else:
                                vals_new = {
                                    'name': writeoff_multi_acc_new_id.name,
                                    'date_maturity': self.date,
                                    'amount_currency': abs(writeoff_multi_acc_new_id.amount),
                                    'currency_id': self.currency_id.id,
                                    'debit': 0.00,
                                    'credit': abs(writeoff_multi_acc_new_id.amount),
                                    'partner_id': self.partner_id.id,
                                    'account_id': writeoff_multi_acc_new_id.writeoff_account_id.id,
                                }
                            new_data_temp.append(vals_new)
                        for credit_line_id in credit_line_ids:
                            print('credit:', credit_line_id['credit'])
                            vals_new = {
                                'name': credit_line_id['name'],
                                'date_maturity': credit_line_id['date_maturity'],
                                'amount_currency': credit_line_id['amount_currency'],
                                'currency_id': credit_line_id['currency_id'],
                                'debit': 0.00,
                                'credit': amount_payment,
                                'partner_id': credit_line_id['partner_id'],
                                'account_id': credit_line_id['account_id'],
                            }
                            new_data_temp.append(vals_new)
                        return new_data_temp
                    elif self.payment_type == 'outbound':
                        print('OUTBOUND')
                        credit_line_ids = list(filter(lambda m: m['credit'], res))
                        debit_line_ids = list(filter(lambda m: m['debit'], res))
                        print('credit_line_ids:', credit_line_ids)
                        print('debit_line_ids:', debit_line_ids)
                        print('==== START')
                        amount_payment = self.amount
                        credit_amount = credit_line_ids[0]['credit']
                        debit_amount = debit_line_ids[0]['debit']
                        for writeoff_multi_acc_new_id in self.writeoff_multi_acc_ids:
                            if writeoff_multi_acc_new_id.amount > 0:
                                amount_payment += abs(writeoff_multi_acc_new_id.amount)
                            else:
                                amount_payment -= abs(writeoff_multi_acc_new_id.amount)
                        print('credit_amount:', credit_amount)
                        print('debit_amount:', debit_amount)
                        print('amount_payment:', amount_payment)
                        for debit_line_id in debit_line_ids:
                            print('DEBIT;', debit_line_id['debit'])
                            vals_new = {
                                'name': debit_line_id['name'],
                                'date_maturity': debit_line_id['date_maturity'],
                                'amount_currency': amount_payment,
                                'currency_id': debit_line_id['currency_id'],
                                'debit': amount_payment,
                                'credit': 0.00,
                                'partner_id': debit_line_id['partner_id'],
                                'account_id': debit_line_id['account_id'],
                            }
                            new_data_temp.append(vals_new)
                        for writeoff_multi_acc_new_id in self.writeoff_multi_acc_ids:
                            print('writeoff_multi_acc_new_id.amount:', writeoff_multi_acc_new_id.amount)
                            if writeoff_multi_acc_new_id.amount > 0:
                                vals_new = {
                                    'name': writeoff_multi_acc_new_id.name,
                                    'date_maturity': self.date,
                                    'amount_currency': abs(writeoff_multi_acc_new_id.amount),
                                    'currency_id': self.currency_id.id,
                                    'debit': 0.00,
                                    'credit': abs(writeoff_multi_acc_new_id.amount),
                                    'partner_id': self.partner_id.id,
                                    'account_id': writeoff_multi_acc_new_id.writeoff_account_id.id,
                                }
                            else:
                                vals_new = {
                                    'name': writeoff_multi_acc_new_id.name,
                                    'date_maturity': self.date,
                                    'amount_currency': abs(writeoff_multi_acc_new_id.amount),
                                    'currency_id': self.currency_id.id,
                                    'debit': abs(writeoff_multi_acc_new_id.amount),
                                    'credit': 0.00,
                                    'partner_id': self.partner_id.id,
                                    'account_id': writeoff_multi_acc_new_id.writeoff_account_id.id,
                                }
                            new_data_temp.append(vals_new)
                        for credit_line_id in credit_line_ids:
                            print('credit:', credit_line_id['credit'])
                            vals_new = {
                                'name': credit_line_id['name'],
                                'date_maturity': credit_line_id['date_maturity'],
                                'amount_currency': credit_line_id['amount_currency'],
                                'currency_id': credit_line_id['currency_id'],
                                'debit': 0.00,
                                'credit': credit_line_id['credit'],
                                'partner_id': credit_line_id['partner_id'],
                                'account_id': credit_line_id['account_id'],
                            }
                            new_data_temp.append(vals_new)
                        print('RETURN---new_data_temp', new_data_temp)
                        return new_data_temp
                    else:
                        print('RETURN---', res)
                        return res
                except:
                    print('EXCEPTTTTTTTTTT')
                    return res




    # code V16 Change - เอา CODE ชุดนี้ออกก่อน
    # #ทับ code ของ STD กรณีคีย์ตรงแล้วระบบมองว่า account ซ้ำ
    # def _synchronize_from_moves(self, changed_fields):
    #     ''' Update the account.payment regarding its related account.move.
    #     Also, check both models are still consistent.
    #     :param changed_fields: A set containing all modified fields on account.move.
    #     '''
    #     if self._context.get('skip_account_move_synchronization'):
    #         return
    #     print('_synchronize_from_moves_CUS')
    #     for pay in self.with_context(skip_account_move_synchronization=True):
    #
    #         # After the migration to 14.0, the journal entry could be shared between the account.payment and the
    #         # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
    #         if pay.move_id.statement_line_id:
    #             continue
    #
    #         move = pay.move_id
    #         move_vals_to_write = {}
    #         payment_vals_to_write = {}
    #
    #         if 'journal_id' in changed_fields:
    #             if pay.journal_id.type not in ('bank', 'cash'):
    #                 raise UserError(_("A payment must always belongs to a bank or cash journal."))
    #
    #         if 'line_ids' in changed_fields:
    #             all_lines = move.line_ids
    #             liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
    #             print('liquidity_lines:',liquidity_lines)
    #             if len(liquidity_lines) != 1:
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "include one and only one outstanding payments/receipts account111111111111.",
    #                     move.display_name,
    #                 ))
    #
    #             if len(counterpart_lines) != 1:
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "include one and only one receivable/payable account (with an exception of "
    #                     "internal transfers).",
    #                     move.display_name,
    #                 ))
    #             #ส่วนที่ ปิด ของ STD
    #             # if writeoff_lines and len(writeoff_lines.account_id) != 1:
    #             #     raise UserError(_(
    #             #         "Journal Entry %s is not valid. In order to proceed, "
    #             #         "all optional journal items must share the same account.",
    #             #         move.display_name,
    #             #     ))
    #
    #             if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "share the same currency.",
    #                     move.display_name,
    #                 ))
    #
    #             if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
    #                 raise UserError(_(
    #                     "Journal Entry %s is not valid. In order to proceed, the journal items must "
    #                     "share the same partner.",
    #                     move.display_name,
    #                 ))
    #
    #             if counterpart_lines.account_id.account_type == 'asset_receivable':
    #                 partner_type = 'customer'
    #             else:
    #                 partner_type = 'supplier'
    #
    #             liquidity_amount = liquidity_lines.amount_currency
    #
    #             move_vals_to_write.update({
    #                 'currency_id': liquidity_lines.currency_id.id,
    #                 'partner_id': liquidity_lines.partner_id.id,
    #             })
    #             payment_vals_to_write.update({
    #                 'amount': abs(liquidity_amount),
    #                 'partner_type': partner_type,
    #                 'currency_id': liquidity_lines.currency_id.id,
    #                 'destination_account_id': counterpart_lines.account_id.id,
    #                 'partner_id': liquidity_lines.partner_id.id,
    #             })
    #             # print('liquidity_amount:',liquidity_amount)
    #             # if liquidity_amount > 0.0:
    #             #     payment_vals_to_write.update({'payment_type': 'inbound'})
    #             # elif liquidity_amount < 0.0:
    #             #     payment_vals_to_write.update({'payment_type': 'outbound'})
    #
    #         move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
    #         # pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))



class writeoff_accounts(models.Model):
    _name = 'writeoff.accounts.line'
    _description = "Multi write off record"

    deduct_item_id = fields.Many2one('account.tax', string='Deduction Item')
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    wht = fields.Boolean(string="WHT", related='writeoff_account_id.wht', default=False)
    # wht_tax = fields.Many2one('account.tax', string="WHT", default=False)
    wht_type = fields.Many2one('account.wht.type', string='WHT Type', )
    name = fields.Char('Description')
    amount_untaxed = fields.Float(string='Full Amount')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount = fields.Float(string='Payment Amount', digits=(16, 2), required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    payment_id = fields.Many2one('account.payment', string='Payment Record')
    wht_reference = fields.Char(string='WHT Reference')


    @api.onchange('deduct_item_id','amount_untaxed')
    # @api.multi
    def _onchange_deduct_item_id(self):
        print ('UPDATE DEDUCT--')
        if self.deduct_item_id:
            tax_account_line_id = self.deduct_item_id.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
            if tax_account_line_id:
                account_id = tax_account_line_id.account_id.id
            else:
                account_id = False
            self.writeoff_account_id = account_id
            self.amt_percent = self.deduct_item_id.amount
            self.name = self.deduct_item_id.name
            self.wht_type = self.deduct_item_id.wht_type
            # if not self.amount_untaxed and self.payment_id.invoice_ids:
            #     self.amount_untaxed = self.payment_id.invoice_ids[0].amount_untaxed
            self.amount = self.amount_untaxed * self.deduct_item_id.amount / 100




