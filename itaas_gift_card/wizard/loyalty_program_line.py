# -*- coding: utf-8 -*-
# Copyright (C) 2020-present ITaas.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    lines_ids = fields.One2many('loyalty.program.line','program_id',string="Lines")



class LoyaltyProgramLine(models.Model):
    _name = 'loyalty.program.line'
    _rec_name = 'ref'

    date_order = fields.Date('วันที่ซื้อ')
    date = fields.Date('วันที่ใช้')
    qty = fields.Float('ยอดที่ซื้อ')
    qty_done = fields.Float('ยอดที่ใช้')
    qty_balance = fields.Float('ยอดยอดคงเหลือ',compute="_compute_qty_balance")
    ref = fields.Char('Order Name')
    pos_order = fields.Many2one('pos.order',string="Pos Order")
    sale_id = fields.Many2one('sale.order',string="Sale Order")
    program_id = fields.Many2one('loyalty.program',string="Program")
    partner_id = fields.Many2one('res.partner',string="Partner")

    @api.depends("qty", "qty_done")
    def _compute_qty_balance(self):
        for obj in self:
            obj.qty_balance = obj.qty - obj.qty_done




