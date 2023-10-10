# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
from datetime import datetime, timedelta, date, time


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_sale_order_line(self):
        if self.origin:
            origin_text = self.origin.split(' - ')
            if len(origin_text) == 2:
                sale_order = origin_text[1]
                sale_id = self.env['sale.order'].search([('name', '=', sale_order)])
                if sale_id:
                    return sale_id.order_line.filtered(lambda x: x.product_id.id == self.product_id.id)

        return False