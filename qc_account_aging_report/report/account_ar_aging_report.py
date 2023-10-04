# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)


from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date, time



class account_ar_aging_report(models.AbstractModel):
    _name = "report.qc_account_aging_report.account_ar_aging_report_id"
    _description = "deposit report"

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        invoice_ids = docs._get_out_invoice()
        if not invoice_ids:
            raise UserError(_("Document is empty."))

        docargs = {
            'doc_ids': docids,
            'data': data['form'],
            'docs': docs,
            'invoice_ids': invoice_ids,
        }
        return docargs