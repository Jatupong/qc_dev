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