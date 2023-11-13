# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.New)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
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

    mr_order_count_one = fields.Integer(string='Order Mr',
                                        # compute='get_sale_count_one'
                                        )






    def action_pre_production(self):
        for obj in self:
            obj.write({'state': 'sent'})

    def action_check_delivery(self):
        for obj in self:
            print(obj)
            self.order_line._validate_analytic_distribution()

            for order in self:
                print('aaaaaaa')
                order.validate_taxes_on_sales_order()
                if order.partner_id in order.message_partner_ids:
                    continue
                order.message_subscribe([order.partner_id.id])

            self.write(self._prepare_confirmation_values())

            # Context key 'default_name' is sometimes propagated up to here.
            # We don't need it and it creates issues in the creation of linked records.
            context = self._context.copy()
            context.pop('default_name', None)

            self.with_context(context)._action_confirm()
            obj.write({'state': 'check_delivery'})

    def action_delivery_confirm(self):
        for obj in self:
            print(obj)
            obj.write({'state': 'delivery_confirm'})

    def action_pp_confirm(self):
        for obj in self:
            print(obj)
            obj.write({'state': 'pp_confirm'})
    # #
    def action_confirm_sale(self):
        print('action_confirm_sale')
        for obj in self:
            obj.write({'state': 'sale'})




    # def _get_forbidden_state_confirm(self):
    #     return {'done', 'cancel'}
    def action_production(self):
        for obj in self:
            print('obj')
            obj.write({'state': 'production'})

    def action_done_sale(self):
        for obj in self:
            print('obj')
            obj.write({'state': 'done'})

    def _action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()
        return self.write({'state': 'cancel'})

    # def action_draft(self):
    #     orders = self.filtered(lambda s: s.state_sale_order in ['cancel', 'sent'])
    #     return orders.write({
    #         'state_sale_order': 'draft',
    #         'signature': False,
    #         'signed_by': False,
    #         'signed_on': False,
    #     })

    def action_do_and_mr(self):
        print('action_do_and_mr')
        #
        for obj in self.order_line:
            # product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
            # print('product_quant',product_quant)
            print('objjjjjj',obj.product_uom_qty)
            print('objjjjjj6666',obj.move_ids)
            print('objjjjjj',obj.move_ids.product_virtual_available)
            print('objjjjjj',obj.move_ids.product_qty_available)
            if not obj.product_id.bom_ids.id:
                raise ValidationError(_("product รายการนี้ยังไม่มี BOM"))

            if obj.move_ids.product_virtual_available < 0:
                print('No product')



        # for sale in self.order_line:
                print('Reserved222', obj)
                so_val = {
                    'custom_product_template_id': obj.product_id.id,
                    'custom_product_qty': obj.product_uom_qty,
                    'end_date': obj.create_date,
                    'custom_date_start_wo': obj.create_date,
                    'custom_product_uom_id': obj.product_uom.id,
                    'custom_bom_id': obj.product_id.bom_ids.id,
                    'sale_order_id':obj.id
                    # 'custom_bom_idh': obj.product_id.variant_bom_ids.id,

                }
                print('so_val',so_val)
                self.env['manufacturing.request.custom'].create(so_val)


    def action_view_mr_order(self):
        print('oooooo')

