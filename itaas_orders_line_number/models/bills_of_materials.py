# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    number = fields.Integer()


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('bom_line_ids', 'bom_line_ids.sequence')
    def get_number(self):
        for obj in self:
            number = 1
            for line in obj.bom_line_ids.filtered(lambda x: x.product_id).sorted(lambda x: x.sequence):
                line.number = number
                number += 1
            obj.is_number_line = True