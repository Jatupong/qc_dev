# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp
from itertools import groupby
from collections import defaultdict
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

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')],
        default='full', required=True, string='Payment Option')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_register_id', string='Write Off Accounts')
    # this is new bank list from res.bank
    bank_cheque = fields.Boolean(string='Is Cheque', related='journal_id.bank_cheque')
    cheque_bank = fields.Many2one('res.bank', string="Bank")
    cheque_branch = fields.Char(string="Branch")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    remark = fields.Char(string="Payment Remark")
    #
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')



    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'

    #payment step
    #1- action_create_payments(self) with action return
    #2-_create_payments
    #3-payment_vals = self._create_payment_vals_from_wizard() or self._create_payment_vals_from_batch(batch_result)
    # to_process.append({
    #     'create_vals': payment_vals,
    #     'to_reconcile': batches[0]['lines'],
    #     'batch': batches[0],
    # })
    #4-payments = self._init_payments(to_process, edit_mode=edit_mode)
    #5-self._post_payments(to_process, edit_mode=edit_mode)
    #6-self._reconcile_payments(to_process, edit_mode=edit_mode)

    def _post_payments(self, to_process, edit_mode=False):
        print('_post_payments:')
        for obj in self:
            payments = self.env['account.payment']
            for vals in to_process:
                print('XXXXXXXXXxx:',vals['payment'])
                payments |= vals['payment']
            for payment in payments:
                if payment.bank_cheque and not payment.cheque_reg_id:
                    print('CREATE_CGEQUE')
                    if payment.partner_type == 'customer':
                        type = 'rec'
                    else:
                        type = 'pay'
                    vals_cheque_rec = {
                        'issue_date': payment.date,
                        'ref': payment.ref,
                        'cheque_bank': obj.cheque_bank.id,
                        'partner_id': obj.partner_id.id,
                        'cheque_branch': obj.cheque_branch,
                        'cheque_number': obj.cheque_number,
                        'cheque_date': obj.cheque_date,
                        'amount': payment.amount,
                        'journal_id': payment.journal_id.id,
                        'user_id': self.env.user.id,
                        'communication': payment.remark,
                        'company_id': payment.env.user.company_id.id,
                        'type': type,
                        'payment_id': payment.id,
                    }
                    payment.cheque_reg_id = self.env['account.cheque.statement'].create(vals_cheque_rec).id
                    if payment.move_id:
                        payment.cheque_reg_id.move_id = payment.move_id.id
            payments.action_post()


    @api.onchange('writeoff_multi_acc_ids')
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            self.amount = self.source_amount - diff_amount
            # self.amount_untaxed = sum([invoice.amount_untaxed for invoice in self.invoice_ids])

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
                 'payment_date')
    def _compute_amount(self):
        active_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)
        for wizard in self:
            print('_compute_amount:')
            if active_model == 'account.move':
                print('source_amount_currency:', wizard.source_amount_currency)
                move_id = self.env[active_model].browse(active_ids)
                if wizard.source_currency_id == wizard.currency_id:
                    print('CASE_1')
                    # Same currency.
                    wizard.amount = wizard.source_amount_currency
                    print('hhhhhh', wizard.source_amount_currency)
                elif move_id[0].currency_id == wizard.currency_id:
                    print('CASE_2')
                    # Payment expressed on the company's currency.
                    wizard.amount = wizard.source_amount
                else:
                    print('CASE_3')
                    # Foreign currency on payment different than the one set on the journal entries.
                    amount_payment_currency = 0
                    for m_id in move_id:
                        amount_payment_currency += m_id.currency_id._convert(m_id.amount_total,
                                                                             wizard.currency_id,
                                                                             wizard.company_id,
                                                                             wizard.payment_date)
                    wizard.amount = amount_payment_currency
            else:
                if wizard.source_currency_id == wizard.currency_id:
                    print('CASE_4')
                    # Same currency.
                    wizard.amount = wizard.source_amount_currency
                elif wizard.currency_id != wizard.company_id.currency_id:
                    print('CASE_5')
                    # Payment expressed on the company's currency.
                    wizard.amount = wizard.source_amount
                else:
                    print('CASE_6')
                    # Foreign currency on payment different than the one set on the journal entries.
                    amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                     wizard.currency_id,
                                                                                     wizard.company_id,
                                                                                     wizard.payment_date)
                    wizard.amount = amount_payment_currency


    @api.depends('amount')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.payment_difference = wizard.source_amount_currency - wizard.amount
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.payment_difference = wizard.source_amount - wizard.amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.payment_difference = amount_payment_currency - wizard.amount

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        print('_create_payments:', res)
        for payment in res:
            payment.bank_cheque = self.bank_cheque
            payment.cheque_bank = self.cheque_bank
            payment.cheque_branch = self.cheque_branch
            payment.cheque_number = self.cheque_number
            payment.cheque_date = self.cheque_date
            payment.remark = self.remark
            if self.writeoff_multi_acc_ids:
                for line in self.writeoff_multi_acc_ids:
                    print('Create writeoff line')
                    self.env['writeoff.accounts.line'].create({
                        'deduct_item_id': line.deduct_item_id.id,
                        'writeoff_account_id': line.writeoff_account_id.id,
                        'wht': line.wht,
                        'wht_type': line.wht_type.id,
                        'name': line.name,
                        'amount': line.amount,
                        'amt_percent': line.amt_percent,
                        'amount_untaxed': line.amount_untaxed,
                        'payment_id': payment.id
                    })
                count = 0
                count_1 = 0
                sum_amount = 0

                print ('len(res.writeoff_multi_acc_ids)',len(res.writeoff_multi_acc_ids))
                if len(res.writeoff_multi_acc_ids) > 1:
                    if payment.payment_type == 'outbound':
                        print('payment.payment_type')
                        account_move_line_obj = self.env['account.move.line']
                        reconcile_invoice = res.reconciled_bill_ids.mapped('line_ids').filtered(
                            lambda x: x.account_id.reconcile)
                        account_move_line_obj |= reconcile_invoice
                        res.line_ids.remove_move_reconcile()
                        line_account_payable = res.line_ids.filtered(lambda
                                                                         x: x.account_id and x.account_id.account_type == 'liability_payable' and x.account_id.reconcile)
                        account_move_line_obj |= line_account_payable
                        reconcile_invoice = res.reconciled_bill_ids.mapped('line_ids').filtered(
                            lambda x: x.account_id.reconcile)
                        for write_off in res.writeoff_multi_acc_ids:
                            if count_1 != 0:
                                sum_amount += write_off.amount + line_account_payable.debit
                            count_1 += 1
                        line_account_payable.with_context(check_move_validity=False).update({'debit': sum_amount, })
                        for write_off in res.writeoff_multi_acc_ids:
                            if count != 0:
                                if write_off.amount > 0:
                                    vals = {
                                        'name': write_off.name,
                                        'debit': 0.00,
                                        'credit': abs(write_off.amount),
                                        'account_id': write_off.writeoff_account_id.id,
                                        'move_id': res.line_ids.move_id.id,
                                        'partner_id': res.partner_id.id,
                                        'wht_tax': write_off.deduct_item_id.id,
                                        'wht_type': write_off.wht_type.id,
                                        'amount_before_tax': write_off.amount_untaxed,
                                        'date_maturity': self.payment_date,
                                    }
                                    print('CASE IF', write_off.amount)
                                    self.env['account.move.line'].with_context(check_move_validity=False).create(vals)
                                else:
                                    vals = {
                                        'name': write_off.name,
                                        'debit': abs(write_off.amount),
                                        'credit': 0.00,
                                        'account_id': write_off.writeoff_account_id.id,
                                        'move_id': res.line_ids.move_id.id,
                                        'partner_id': res.partner_id.id,
                                        'wht_tax': write_off.deduct_item_id.id,
                                        'wht_type': write_off.wht_type.id,
                                        'amount_before_tax': write_off.amount_untaxed,
                                        'date_maturity': self.payment_date,
                                    }
                                    print('CASE ELSE', write_off.amount)
                                    self.env['account.move.line'].with_context(check_move_validity=False).create(vals)
                            count += 1
                        account_move_line_obj.reconcile()
                    else:
                        print('TYPE INBOUND')
                        account_move_line_obj = self.env['account.move.line']
                        reconcile_invoice = res.reconciled_invoice_ids.mapped('line_ids').filtered(
                            lambda x: x.account_id.reconcile)
                        account_move_line_obj |= reconcile_invoice
                        res.line_ids.remove_move_reconcile()
                        line_account_payable = res.line_ids.filtered(lambda x: x.account_id and x.account_id.account_type == 'asset_receivable' and x.account_id.reconcile)
                        account_move_line_obj |= line_account_payable
                        print('line_account_payable:',line_account_payable)
                        print('account_move_line_obj:',account_move_line_obj)
                        reconcile_invoice = res.reconciled_bill_ids.mapped('line_ids').filtered(
                            lambda x: x.account_id.reconcile)
                        for write_off in res.writeoff_multi_acc_ids:
                            if count_1 != 0:
                                sum_amount += write_off.amount + line_account_payable.credit
                            count_1 += 1
                        print('sum_amount:',sum_amount)
                        line_account_payable.with_context(check_move_validity=False).update({'credit': sum_amount})
                        for write_off in res.writeoff_multi_acc_ids:
                            print('write_off:',write_off)
                            if count != 0:
                                if write_off.amount > 0:
                                    vals = {
                                        'name': write_off.name,
                                        'debit': abs(write_off.amount),
                                        'credit': 0.00,
                                        'account_id': write_off.writeoff_account_id.id,
                                        'move_id': res.line_ids.move_id.id,
                                        'partner_id': res.partner_id.id,
                                        'wht_tax': write_off.deduct_item_id.id,
                                        'wht_type': write_off.wht_type.id,
                                        'amount_before_tax': write_off.amount_untaxed,
                                        'date_maturity': self.payment_date,
                                    }
                                    print('CASE IF', write_off.amount)
                                    self.env['account.move.line'].with_context(check_move_validity=False).create(vals)
                                else:
                                    vals = {
                                        'name': write_off.name,
                                        'debit': 0.00,
                                        'credit': abs(write_off.amount),
                                        'account_id': write_off.writeoff_account_id.id,
                                        'move_id': res.line_ids.move_id.id,
                                        'partner_id': res.partner_id.id,
                                        'wht_tax': write_off.deduct_item_id.id,
                                        'wht_type': write_off.wht_type.id,
                                        'amount_before_tax': write_off.amount_untaxed,
                                        'date_maturity': self.payment_date,
                                    }
                                    print('CASE ELSE', write_off.amount)
                                    self.env['account.move.line'].with_context(check_move_validity=False).create(vals)
                            count += 1
                        print('account_move_line_obj:',account_move_line_obj)
                        account_move_line_obj.reconcile()

            # update wht number
            if payment.move_id:
                payment.move_id.action_gen_wht()
        return res

    def _create_payment_vals_from_wizard(self,batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        print('_create_payment_vals_from_wizard',res)
        if self.writeoff_multi_acc_ids:
            write_off_line_ids = {}
            line_ids_new = []
            count = 0
            for write_off_line in self.writeoff_multi_acc_ids:
                print('write_off_line:',write_off_line)
                print('write_off_line:',write_off_line.deduct_item_id)
                print('write_off_line:',write_off_line.wht_type)
                if count == 0:
                    print('COUNT == 0')

                    if res['payment_type'] == 'inbound': #this in inbound invoice
                        write_off_line_ids.update({
                            'name': write_off_line.name,
                            # 'amount': write_off_line.amount,

                            'balance': write_off_line.amount,
                            'debit': abs(write_off_line.amount) if write_off_line.amount > 0 else 0.00,
                            'credit': abs(write_off_line.amount) if write_off_line.amount < 0 else 0.00,
                            'partner_id': self.partner_id.id,
                            'account_id': write_off_line.writeoff_account_id.id,
                            'wht_tax': write_off_line.deduct_item_id.id,
                            'wht_type': write_off_line.wht_type.id,
                            'amount_before_tax': write_off_line.amount_untaxed,
                            'date_maturity': self.payment_date,
                            'amount_currency': write_off_line.amount,
                            'currency_id': write_off_line.currency_id.id,

                        })
                    else: #this is outbound, bill
                        print ('COME HERE---------')
                        write_off_line_ids.update({
                            'name': write_off_line.name,
                            # 'amount': write_off_line.amount,

                            'balance': write_off_line.amount * (-1),
                            'debit': abs(write_off_line.amount) if write_off_line.amount < 0 else 0.00,
                            'credit': abs(write_off_line.amount) if write_off_line.amount > 0 else 0.00,
                            'partner_id': self.partner_id.id,
                            'account_id': write_off_line.writeoff_account_id.id,
                            'wht_tax': write_off_line.deduct_item_id.id,
                            'wht_type': write_off_line.wht_type.id,
                            'amount_before_tax': write_off_line.amount_untaxed,
                            'date_maturity': self.payment_date,
                            'amount_currency': write_off_line.amount * (-1),
                            'currency_id': write_off_line.currency_id.id,

                        })

                count += 1
            print('line_ids_new:',line_ids_new)
            print ('END With write off',write_off_line_ids)
            res['write_off_line_vals'] = [write_off_line_ids]

        return res



class writeoff_accounts(models.TransientModel):
    _name = 'writeoff.accounts'
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

    # new for payment wizard only.
    payment_register_id = fields.Many2one('account.payment.register', string='Payment Record')
    # payment_billing_id = fields.Many2one('register.billing.payments', string='Payment Record')
    # department_id = fields.Many2one('hr.department', string='Department')

    @api.onchange('writeoff_account_id')
    # @api.multi
    def _onchange_writeoff_account_id(self):
        if self.writeoff_account_id:
            self.name = self.writeoff_account_id.name

    @api.onchange('amt_percent','amount_untaxed')
    def _onchange_amt_percent(self):
        if self.amount_untaxed and self.amt_percent:
            self.amount = self.amount_untaxed * self.amt_percent / 100

    @api.onchange('deduct_item_id')
    def _onchange_deduct_item_id(self):
        print('UPDATE DEDUCT--')
        print('self.env.context:', self.env.context)
        if 'params' in self.env.context:
            print('CASEEEEEE_1')
            active = self.env.context.get("active_ids")
            model = self.env.context.get("params").get("model")
            if model == 'account.move':
                move_obj = self.env['account.move'].browse(active)
                print('move_obj:', move_obj)
                self.amount_untaxed = move_obj.amount_untaxed
            else:
                self.amount_untaxed = self.payment_register_id.source_amount
        elif 'active_id' in self.env.context and 'params' not in self.env.context:
            print('CASEEEEEE_2')
            active = self.env.context.get("active_ids")
            model = self.env.context.get("active_model")
            if model == 'account.move':
                move_obj = self.env['account.move'].browse(active)
                print('move_obj:', move_obj)
                self.amount_untaxed = sum(move_obj.mapped('amount_untaxed'))
            else:
                self.amount_untaxed = self.payment_register_id.source_amount
        else:
            print('CASEEEEEE_3')
            self.amount_untaxed = self.payment_register_id.source_amount
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
            # self.amount_untaxed = self.payment_id.invoice_ids[0].amount_untaxed
            self.amount = self.amount_untaxed * self.deduct_item_id.amount / 100
