# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.
from odoo import fields, models, _, api
import html
from datetime import datetime, timedelta
from datetime import datetime

from odoo.tools.safe_eval import pytz


class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_sale_details(self):
        start_at=self.start_at+ timedelta(hours=7)
        stop_at = self.stop_at + timedelta(hours=7)
        cur = datetime.now() + timedelta(hours=7)
        cur=cur.strftime("%Y-%m-%d %H:%M:%S")
        for session in self:
            vals = {}
            final_list = []
            for line_id in session.order_ids.lines.filtered(
                    lambda line: line.product_id.type != "service" and line.qty > 0):

                if line_id.order_id.state == 'cancel':
                    continue
                if line_id.product_id.id not in vals:
                    vals[line_id.product_id.id] = {
                        'name': line_id.full_product_name,
                        'qty': line_id.qty,
                        'uom': line_id.product_uom_id.name,
                        'amount': line_id.price_subtotal,
                        'start_at':start_at,
                        'stop_at':stop_at,
                        'cur':cur,
                    }
                else:
                    vals[line_id.product_id.id]['amount'] += line_id.price_subtotal_incl
                    vals[line_id.product_id.id]['qty'] += line_id.qty
            for a in vals:
                final_list.append(vals.get(a))
            print("finallist", final_list)
            return final_list

    # def get_order_details(self):
    #     orders = self.env['pos.order'].search([('session_id', '=', self.name)])
    #     order_name = [order.name for order in orders]
    #     return order_name

    def get_session_payment_details(self):
        payments = self.env['pos.payment'].search([('session_id', '=', self.name)])
        cash = 0
        bank = 0
        return_cash = 0
        for payment in payments:
            if payment.amount > 0:
                if payment.payment_method_id.is_cash_count:
                    cash += payment.amount
                else:
                    bank += payment.amount
            else:
                return_cash += payment.amount
        # return_cash = round(return_cash, 2)
        data = {'cash_amount': cash, 'bank_amount': bank, 'return_amount': return_cash}
        return data

    def get_payment_method_amounts(self):
        order_payments = self.env['pos.payment'].search([('session_id', '=', self.name)])
        payment_data = {}
        for pay in order_payments:
            if pay.payment_method_id.name not in payment_data:
                payment_data.update({pay.payment_method_id.name: pay.amount})
            else:
                payment_data[pay.payment_method_id.name] += pay.amount
        return payment_data

    def cash_register_txn_amount(self):
        txn = 0
        for line in self.cash_register_id.line_ids:
            txn += line.amount
        return txn

    # def cashbox_denomination(self):
    #     print("CASHREGISTER", self.cash_register_id)
    #     # print("messages",self.message_ids)
    #     h = html.parser
    #     for message in self.message_ids:
    #         ccc = h.unescape(message.body)
    #         message = str(ccc).replace('<p>', '').replace('<br>', '').replace('</p>', '').replace('Money details',
    #                                                                                               '').replace(' ', '')
    #         print(type(message), message)
    #         idx1 = message.index('-')
    #         # print("...........",message.subject, message.body)
    #     # message_name = [message.subject for message in self.message_ids]
    #     # print("mesages",message_name)
    #     cashregisterbox = self.env['account.cashbox.line'].search([])
    #     print("cashregisterbox", cashregisterbox)
    #     bill_values = []
    #     print("selsssssssss", self.cash_register_id.cashbox_end_id)
    #     for line in self.cash_register_id.cashbox_end_id.cashbox_lines_ids:
    #         bill_values.append((line.coin_value, line.number))
    #     print("billvalues", bill_values)
    #     return bill_values
