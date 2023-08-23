# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetMoveWizard(models.TransientModel):
    _name = "asset.move.wizard"
    _description = "Asset Movement Wizard"

    from_location_id = fields.Many2one('asset.location', 'From Location')
    from_department_id = fields.Many2one('hr.department', 'From Department')
    from_employee_id = fields.Many2one('hr.employee', 'From Employee')
    # domain = "[('state', '=', 'model'), ('user_type_id', '=?', user_type_id), ('asset_type', '=', asset_type)]" / >
    from_model_id = fields.Many2one('account.asset', string='From Category', domain="[('company_id', '=', company_id)]")

    to_location_id = fields.Many2one('asset.location', 'To Location')
    to_department_id = fields.Many2one('hr.department', 'To Department')
    to_employee_id = fields.Many2one('hr.employee', 'To Employee')
    to_category_id = fields.Many2one('account.asset', string='To Category')
    to_model_id = fields.Many2one('account.asset', string='To Category', domain="[('company_id', '=', company_id)]")

    date = fields.Date(string='Date',default=fields.datetime.today())
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.model
    def default_get(self, fields):
        active_id = self.env.context.get("active_ids", False)
        res = super(AssetMoveWizard, self).default_get(fields)
        # print ('EMPLOYEEE')
        # print (active_id)
        asset_id = self.env['account.asset'].browse(active_id)
        # print (asset_id.employee_id)
        res.update({'from_location_id': asset_id.location_id.id, 'from_employee_id': asset_id.employee_id.id, 'from_department_id': asset_id.department_id.id,'from_model_id': asset_id.model_id.id})
        return res

    def action_validate(self):
        active_id = self.env.context.get("active_ids", False)
        asset_id = self.env['account.asset'].browse(active_id)
        val = {
            'from_location_id': self.from_location_id.id if self.to_location_id else False,
            'from_employee_id': self.from_employee_id.id if self.to_employee_id else False,
            'from_department_id': self.from_department_id.id if self.to_department_id else False,
            # 'from_model_id': self.from_model_id.id if self.to_model_id else False,
            'to_location_id': self.to_location_id and self.to_location_id.id or False,
            'to_employee_id': self.to_employee_id and self.to_employee_id.id or False,
            'to_department_id': self.to_department_id and self.to_department_id.id or False,
            # 'to_model_id': self.to_model_id and self.to_model_id.id or False,
            'asset_id': asset_id.id,
            'date': self.date,
        }
        if self.to_location_id:
            asset_id.update({'location_id': self.to_location_id.id})
        if self.to_employee_id:
            asset_id.update({'employee_id': self.to_employee_id.id})
        if self.to_department_id:
            asset_id.update({'department_id': self.to_department_id.id})
        # if self.to_model_id:
        #     asset_id.update({'model_id': self.to_model_id.id})

        self.env['asset.move'].create(val)

    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     invoice_vals = {
    #         'ref': order.client_order_ref,
    #         'type': 'out_invoice',
    #         'invoice_origin': order.name,
    #         'invoice_user_id': order.user_id.id,
    #         'narration': order.note,
    #         'partner_id': order.partner_invoice_id.id,
    #         'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
    #         'partner_shipping_id': order.partner_shipping_id.id,
    #         'currency_id': order.pricelist_id.currency_id.id,
    #         'invoice_payment_ref': order.reference,
    #         'invoice_payment_term_id': order.payment_term_id.id,
    #         'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
    #         'team_id': order.team_id.id,
    #         'campaign_id': order.campaign_id.id,
    #         'medium_id': order.medium_id.id,
    #         'source_id': order.source_id.id,
    #         'invoice_line_ids': [(0, 0, {
    #             'name': name,
    #             'price_unit': amount,
    #             'quantity': 1.0,
    #             'product_id': self.product_id.id,
    #             'product_uom_id': so_line.product_uom.id,
    #             'tax_ids': [(6, 0, so_line.tax_id.ids)],
    #             'sale_line_ids': [(6, 0, [so_line.id])],
    #             'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
    #             'analytic_account_id': order.analytic_account_id.id or False,
    #         })],
    #     }
    #
    #     return invoice_vals



