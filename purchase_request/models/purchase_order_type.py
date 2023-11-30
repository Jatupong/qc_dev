# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, exceptions, fields, models

class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    requests_order_type = fields.Many2one('order.type', string="Order Type")
    # tax_type_purchase = fields.Many2one('purchase.tax.type', string="Tax Type")

