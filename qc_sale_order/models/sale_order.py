# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_set_line_ids = fields.One2many('sale.order.set.line','order_id',string='Order Line Set')

    def apply_set(self):
        if self.sale_order_set_line_ids:
            self.sale_order_set_line_ids.unlink()
        order_line_set = self.order_line.filtered(lambda p: p.product_template_id.is_set)
        for order_line in order_line_set:
            for set_line_id in order_line.product_template_id.product_set_lines:
                val_set_line = {
                    'product_set_id': order_line.product_id.id,
                    'sale_order_line_id': order_line.id,
                    'order_id': order_line.order_id.id,
                    'product_id': set_line_id.product_id.id,
                    'uom_id': set_line_id.uom_id.id,
                    'original_set_qty': set_line_id.qty,
                    'qty': set_line_id.qty * order_line.product_uom_qty,
                }
                self.env['sale.order.set.line'].create(val_set_line)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_cost = fields.Float(string='ผลิตภัณท์')
    commission_cost = fields.Float(string='คอม')
    box_cost = fields.Float(string='กล่อง')
    sticker_cost = fields.Float(string='สติ๊กเกอร์')
    cost_1 = fields.Float(string='ราคา1')
    cost_2 = fields.Float(string='ราคา2')
    cost_3 = fields.Float(string='ราคา3')
    G_W_KGS = fields.Float(string='G.W. KGS.')
    N_W_KGS = fields.Float(string='N.W. KGS.')


class SaleOrderSetLine(models.Model):
    _name = 'sale.order.set.line'

    product_set_id = fields.Many2one('product.product',string='Product Set ID')
    sale_order_line_id = fields.Many2one('sale.order.line',string='Sale Line')
    order_id = fields.Many2one('sale.order', string='Sales Order')
    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('uom.uom',string='Unit of Measure')
    qty = fields.Float(string='Quantity')
    original_set_qty = fields.Float(string='Set Quantity')
    product_cost = fields.Float(string='ผลิตภัณท์')
    commission_cost = fields.Float(string='คอม')
    box_cost = fields.Float(string='กล่อง')
    sticker_cost = fields.Float(string='สติ๊กเกอร์')
    cost_1 = fields.Float(string='ราคา1')
    cost_2 = fields.Float(string='ราคา2')
    cost_3 = fields.Float(string='ราคา3')
    # G_W_KGS = fields.Float(string='G.W. KGS.')
    # N_W_KGS = fields.Float(string='N.W. KGS.')