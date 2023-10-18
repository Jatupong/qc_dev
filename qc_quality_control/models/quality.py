# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
from datetime import datetime, timedelta, date, time


class QualityCheck(models.Model):
    _inherit = "quality.check"

    def _prepare_quality_alert(self):
        value = {
            'check_id': self.id,
            'product_id': self.product_id.id,
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'lot_id': self.lot_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'company_id': self.company_id.id,
            'production_id': self.production_id.id,
            'production_qty': self.production_id.product_qty,
            'mo_date_planned_start': self.production_id.date_planned_start,
        }

        return value

    def do_alert(self):
        self.ensure_one()
        alert = self.env['quality.alert'].create(self._prepare_quality_alert())
        return {
            'name': _('Quality Alert'),
            'type': 'ir.actions.act_window',
            'res_model': 'quality.alert',
            'views': [(self.env.ref('quality_control.quality_alert_view_form').id, 'form')],
            'res_id': alert.id,
            'context': {'default_check_id': self.id},
        }