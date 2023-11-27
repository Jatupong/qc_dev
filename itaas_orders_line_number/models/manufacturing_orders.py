# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ManufacturingOrdersLine(models.Model):
    _inherit = 'stock.move'

    number = fields.Integer()


class ManufacturingOrders(models.Model):
    _inherit = 'mrp.production'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('move_raw_ids', 'move_raw_ids.sequence')
    def get_number(self):
        for obj in self:
            number = 1
            for line in obj.move_raw_ids.filtered(lambda x: x.product_id).sorted(lambda x: x.sequence):
                line.number = number
                number += 1
            obj.is_number_line = True