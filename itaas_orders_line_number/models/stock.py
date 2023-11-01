# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    number = fields.Integer()

    # description_picking = fields.Text(string="Description Picking", related="move_id.description_picking" ,readonly=False)
    description_picking = fields.Text(string="Description Picking", related="move_id.sale_line_id.name" ,readonly=False)



class StockMove(models.Model):
    _inherit = 'stock.move'

    number = fields.Integer()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_consignee = fields.Many2one('res.partner',
                    string="consignee",
                    )

    # shipping_mark = fields.Many2one('res.partner',
    #                 string="shipping mark",
    #                 )

    shipping_mark = fields.Text()

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('move_lines', 'move_lines.sequence', 'move_line_ids')
    def get_number(self):
        for obj in self:
            number = 1
            for sm in obj.move_lines.filtered(lambda x: x.product_id).sorted(lambda x: x.sequence):
                sm.number = number
                number += 1
            number = 1
            for sml in obj.move_line_ids.filtered(lambda x: x.product_id).sorted(lambda x: x.id):
                sml.number = number
                number += 1
            obj.is_number_line = True








