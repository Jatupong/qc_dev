# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)


from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date, time



class deposit_report(models.AbstractModel):
    _name = "report.qc_deposit_report.deposit_report_id"
    _description = "deposit report"

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        date_from_time = docs.convert_usertz_to_utc(
            datetime.combine(fields.Date.from_string(docs.date_from), time.min))
        date_to_time = docs.convert_usertz_to_utc(datetime.combine(fields.Date.from_string(docs.date_to), time.max))
        sale_order_ids = docs._get_is_downpayment(date_from_time, date_to_time)
        if not sale_order_ids:
            raise UserError(_("Document is empty."))
        partner_ids = sale_order_ids.mapped('partner_id')

        docargs = {
            'doc_ids': docids,
            'data': data['form'],
            'docs': docs,
            'sale_order_ids': sale_order_ids,
            'partner_ids': partner_ids,
        }
        return docargs

    # def _get_is_downpayment(self,partner_ids):
    #     domain = [('is_downpayment', '=', True),
    #               ('state', 'in', ['sale', 'done']),
    #               # ('scheduled_date', '<=', date_from_time),
    #               # ('scheduled_date', '>=', date_to_time)
    #     ]
    #
    #     if partner_ids:
    #         domain += [('order_partner_id', '=', partner_ids.ids)]
    #
    #     return self.env['sale.order.line'].search(domain).mapped('order_id')

    # def Chack_Data(self,partner,partner_ids):
    #     sale_order_ids = self._get_is_downpayment(partner_ids)
    #     sale_order_ids_by_partners = sale_order_ids.filtered(lambda x: x.partner_id.id == partner.id)
    #     sale_order_ids_by_partner = sale_order_ids_by_partners.filtered(lambda x: x.name).sorted(key=lambda a: a.name)
    #     chack1 = []
    #     chack2 = []
    #     chack3 = 0
    #     for sale in sale_order_ids_by_partner:
    #         chack1.append(sale.id)
    #         chack_sale_name = []
    #         a = datetime.strptime(date_from_time, '%Y-%m-%d %H:%M:%S')
    #         a = a.date()
    #         for inv in sale.invoice_ids.filtered(lambda x: x.name).sorted().sorted(key=lambda a: a.name):
    #             if inv.state == 'posted':
    #                 payment_name = True
    #                 label = []
    #                 for i in inv.invoice_line_ids:
    #                     if 'Down payment' != i.product_id.name:
    #                         payment_name = False
    #                     label.append(i.name)
    #                 if inv.invoice_date < a:
    #                     if sale.id not in chack2:
    #                         chack2.append(sale.id)
    #                     continue
    #
    #                 if payment_name:
    #                     if not (sale.name in chack_sale_name):
    #                         chack3 += 1
    #
    #     if chack1 != chack2 and chack3 > 0:
    #         return True