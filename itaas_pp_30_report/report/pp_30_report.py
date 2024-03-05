# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)


from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date, time


class pp_30_report(models.AbstractModel):
    _name = "report.itaas_pp_30_report.pp_30_report_id"
    _description = "pp 30 report"

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        data_results = docs._get_result_report()



        docargs = {
            'doc_ids': docids,
            'data': data['form'],
            'docs': docs,
            'data_results': data_results,
        }
        return docargs