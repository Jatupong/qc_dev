# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=[
            ('draft', "Draft Order"),
            ('sent', "Pre-production order"),
            ('production', "Production order"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')




    # # partner_state = fields.Selection(
    # #     '_get_partner_states',
    # #     string='Partner State',
    # #     readonly=True,
    # #     required=True,
    # #     default='active'
    # # )
    #
    # partner_state_sale = fields.Selection(
    #     '_get_partner_states_sale',
    #     string='Partner State',
    #     readonly=True,
    #     required=True,
    #     default='draft order'
    # )
    #
    # @api.model
    # def _get_partner_states_sale(self):
    #     return [
    #         ('draft_order', _('Draft Order')),
    #         ('pre_production_order', _('PRE-PRODUCTION ORDER')),
    #         ('sale_order', _('SALE ORDER')),
    #         ('production_order', _('PRODUCTION ORDER'))]
    #
    # # @api.model
    # # def _get_partner_states(self):
    # #     return [
    # #         ('draft order', _('Draft Order')),
    # #         ('pre-production order', _('PRE-PRODUCTION ORDER')),
    # #         ('sale order', _('SALE ORDER')),
    # #         ('production order', _('PRODUCTION ORDER'))]
    #
    # # def action_partner_active(self):
    # #     for obj in self:
    # #         obj.write({'partner_state': 'active'})
    # #
    # # def action_partner_inactive(self):
    # #     for obj in self:
    # #         obj.write({'partner_state': 'inactive'})
    # #
    # # def action_partner_on_hold(self):
    # #     for obj in self:
    # #         obj.write({'partner_state': 'on_hold'})
    # #
    # # def action_partner_draft(self):
    # #     for obj in self:
    # #         obj.write({'partner_state': 'draft'})
    #
    #
    #
    # def action_partner_draft_order_sale(self):
    #     for obj in self:
    #         obj.write({'partner_state_sale': 'draft order'})
    #
    # def action_partner_pre_production_order_sale(self):
    #     for obj in self:
    #         obj.write({'partner_state_sale': 'pre production order'})
    #
    # def action_partner_sale_order_sale(self):
    #     for obj in self:
    #         obj.write({'partner_state_sale': 'sale order'})
    #
    # def action_partner_production_order_sale(self):
    #     for obj in self:
    #         obj.write({'partner_state_sale': 'production order'})