# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_in_svl_vals(self, forced_quantity):
        svl_vals_list = super(StockMove, self)._get_in_svl_vals(forced_quantity)
        for val in svl_vals_list:
            move = self.env['stock.move'].browse(val['stock_move_id'])
            print('move.purchase_line_id ', move.purchase_line_id)
            print('move.picking_id.purchase_id ', move.picking_id.purchase_id)
            if not move.purchase_line_id and move.picking_id.purchase_id:
                val['unit_cost'] = 0.0
                val['value'] = 0.0

        print('_get_in_svl_vals', svl_vals_list)
        return svl_vals_list