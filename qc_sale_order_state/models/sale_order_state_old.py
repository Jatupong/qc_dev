# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.New)

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state_sale_order = fields.Selection(
        selection=[
            ('draft', "Draft Order"),
            ('sent', "Pre-production order"),
            ('check_delivery', "Check Deliveryr"),
            ('delivery_confirm', "Delivery Confirm"),
            ('pp_confirm', "PP Confirm"),
            ('sale', "Sales Order"),
            ('production', "Production order"),
            ('done', "Done"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')






    def action_pre_production(self):
        for obj in self:
            obj.write({'state_sale_order': 'sent'})

    def action_pre_production(self):
        for obj in self:
            print(obj)
            # obj.write({'state_sale_order': 'sent'})

    def action_pre_production(self):
        for obj in self:
            print(obj)
            # obj.write({'state_sale_order': 'sent'})

    def action_pre_production(self):
        for obj in self:
            print(obj)
            # obj.write({'state_sale_order': 'sent'})
    # #
    def action_confirm_sale(self):
        print('action_confirm_sale')
        for obj in self:
            # self.order_line._validate_analytic_distribution()
            #
            # for order in self:
            #     print('aaaaaaa')
            #     order.validate_taxes_on_sales_order()
            #     if order.partner_id in order.message_partner_ids:
            #         continue
            #     order.message_subscribe([order.partner_id.id])
            #
            # self.write(self._prepare_confirmation_values())
            #
            # # Context key 'default_name' is sometimes propagated up to here.
            # # We don't need it and it creates issues in the creation of linked records.
            # context = self._context.copy()
            # context.pop('default_name', None)
            #
            # self.with_context(context)._action_confirm()


            obj.write({'state_sale_order': 'sale'})




    def _get_forbidden_state_confirm(self):
        return {'done', 'cancel'}
    def action_production(self):
        for obj in self:
            obj.write({'state_sale_order': 'production'})

    def action_done_sale(self):
        for obj in self:
            obj.write({'state_sale_order': 'done'})

    def _action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()
        return self.write({'state_sale_order': 'cancel'})

    def action_draft(self):
        orders = self.filtered(lambda s: s.state_sale_order in ['cancel', 'sent'])
        return orders.write({
            'state_sale_order': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    def action_do_and_mr(self):
        print('action_do_and_mr')
        #
        # for obj in self.order_line:
        #     product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
        #     print('product_quant',product_quant)
        #     print('objjjjjj',obj.product_uom_qty)
        #     print('objjjjjj',obj.move_ids)


        # for sale in self.order_line:
        #     print('Reserved222', sale)
        #     so_val = {
        #         'custom_product_template_id': sale.product_id.id,
        #         'custom_product_qty': sale.product_uom_qty,
        #         'end_date': sale.create_date,
        #         'custom_date_start_wo': sale.create_date,
        #         'custom_bom_id': sale.product_id.variant_bom_ids[0].id,
        #
        #     }
        #     print('so_val',so_val)
        #     self.env['manufacturing.request.custom'].create(so_val)





    #     for obj in self.order_line:
    #         product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
    #         print('product_quant',product_quant)
    #         print('objjjjjj',obj.product_uom_qty)
    #         print('objjjjjj',obj.move_ids)
    #     #     obj.write({'state_sale_order': 'done'})
    #
    # #         obj.write({'partner_state_sale': 'production order'})