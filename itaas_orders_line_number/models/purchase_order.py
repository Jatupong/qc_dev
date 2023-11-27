# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    number = fields.Integer()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_number_line = fields.Boolean(compute='get_number', store=True, compute_sudo=True)
    branch_no = fields.Char(string="Branch")


    @api.onchange('partner_id')
    def _onchange_branch_no(self):
        self.branch_no = self.partner_id.branch_no

    @api.depends('order_line', 'order_line.sequence')
    def get_number(self):
        print('get_number')
        for obj in self:
            number = 1
            for line in obj.order_line.filtered(lambda x: x.product_id).sorted(lambda x: x.sequence):
                line.number = number
                print('ddddddd',number)
                number += 1
            obj.is_number_line = True