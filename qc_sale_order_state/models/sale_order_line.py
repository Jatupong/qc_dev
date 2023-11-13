# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.New)

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    manufacturing_request_ids = fields.One2many("manufacturing.request.custom", "sale_order_id", string="Manufacturing Request")