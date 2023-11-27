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

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for production in self:
            move_ids = production.picking_ids.mapped('move_ids').filtered(lambda x:x.product_id.id in production.move_raw_ids.mapped('product_id').ids)
            # print('production.picking_ids', production.picking_ids)
            # print('move_ids', move_ids)
            for move in move_ids:
                if move.bom_line_id.bom_id.percent_yield:
                    percent_yield = move.bom_line_id.bom_id.percent_yield
                    new_product_uom_qty = move.product_uom_qty + (move.product_uom_qty * percent_yield * 0.01)
                    move.update({'product_uom_qty': new_product_uom_qty})

        return res