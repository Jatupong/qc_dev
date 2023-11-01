# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class SalesOrderLine(models.Model):
    _inherit = 'account.move.line'

    number = fields.Integer()


#
class SalesOrder(models.Model):
    _inherit = 'account.move'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)

    @api.depends('attribute_line_ids', 'attribute_line_ids.sequence','name')
    def get_number(self):
        print('invoice')
        for obj in self:
            print('obj:',obj)
            number = 1
            if obj.move_type != 'entry':
                for line in obj.invoice_line_ids.filtered(lambda x: x.name or x.product_id).sorted(lambda x: x.sequence):
                    print('line:',line)
                    line.with_context({"check_move_validity": False}).number = number
                    number += 1
                obj.with_context({"check_move_validity": False}).is_number_line = True
