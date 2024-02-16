# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # reverse tax
    is_reverse_tax = fields.Boolean(string='Reverse Tax')

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        print('_create_payments_CUSTOME:',res)
        if self.is_reverse_tax:
            for payment in res:
                payment.is_reverse_tax = True
                if payment.is_reverse_tax:
                    print('1.1')
                    print('1.1',payment.reconciled_bill_ids)
                    print('1.1',payment.reconciled_invoice_ids)
                    if payment.reconciled_bill_ids:
                        print('1.2')
                        for bill_id in payment.reconciled_bill_ids:
                            print('invoice_1_3:',bill_id)
                            move_id = bill_id.action_invoice_generate_tax_invoice()
                            print('move_id_last:',move_id)
                            if move_id:
                                print('move_id:',move_id.line_ids)
                                for mve in move_id.line_ids:
                                    mve.update({'payment_id': payment.id})
                    elif payment.reconciled_invoice_ids:
                        for invoice in payment.reconciled_invoice_ids:
                            print('invoice_1_4:',invoice)
                            move_id = invoice.action_invoice_generate_tax_invoice()
                            if move_id:
                                move_id.line_ids.update({'payment_id': payment.id})

        # print(aaa)
        return res

class AccountPayment(models.Model):
    _inherit = "account.payment"

    # reverse tax
    is_reverse_tax = fields.Boolean(string='Reverse Tax')

    def post(self):
        print('post')
        for payment in self:
            print('payment:',payment)
            print('payment:',payment.is_reverse_tax)
            rec = super(AccountPayment, payment).post()
            if payment.is_reverse_tax:
                print('is_reverse_tax:')
                for invoice in self.invoice_ids:
                    move_id = invoice.action_invoice_generate_tax_invoice()
                    if move_id:
                        move_id.line_ids.update({'payment_id': payment.id})

            return rec


