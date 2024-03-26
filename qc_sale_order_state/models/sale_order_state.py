# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.New)
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=[
            ('draft', "Draft Order"),
            ('sent', "Pre-production order"),
            ('check_delivery', "Check Delivery"),
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
                                        compute='get_sale_count_one'
                                        )

    mr_order_sale_ids = fields.Many2many(
        comodel_name='sale.order.line',
        string="Sale",
        compute='get_sale_count_one',
        copy=False)

    attn_id = fields.Many2one('res.partner', string="Attn")
    cc_id = fields.Many2one('res.partner', string="CC")

    delivery_exp_date = fields.Date(string="วันหมดอายุส่งมอบ")

    delivery_date = fields.Datetime(string="Delivery Date" ,readonly=True ,compute='_compute_deliverydate')
    delivery_date_week = fields.Char(string="Delivery Date Week")




    @api.depends('order_line.invoice_lines')
    def get_sale_count_one(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            mr = order.order_line.manufacturing_request_ids.sale_order_id.filtered(
                lambda r: r.order_id.id == self.id)
            print('invoices_mr', mr)
            order.mr_order_sale_ids = mr
            order.mr_order_count_one = len(mr)
            print('order_mr',len(mr))






    def _compute_deliverydate(self):
        for data in self:
            data.delivery_date = data.commitment_date
            try:
                data.update_week()
            except:
                pass


    @api.onchange('commitment_date')
    def _onchange_model_id(self):
        for data in self:
            data.delivery_date = data.commitment_date






    def action_pre_production(self):
        # for obj in self:
        #     obj.write({'state': 'sent'})

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


            # obj.write({'state': 'check_delivery'})
            obj.write({'state': 'sent'})

            for obj in self.order_line:
                # product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
                # print('product_quant',product_quant)
                # print('objjjjjj', obj.product_uom_qty)
                # print('objjjjjj6666', obj.move_ids)
                # print('objjjjjj', obj.move_ids.product_virtual_available)
                # print('objjjjjj', obj.move_ids.product_qty_available)
                if not obj.product_id.bom_ids:
                    raise ValidationError(_("product รายการนี้ยังไม่มี BOM"))

                msg ="Err!"
                Zum =0

                try:
                    msg+='obj.move_ids {}\n'.format(obj.move_ids.ids)
                    for i in obj.move_ids:
                        msg +='product_uom_qty {} reserved_availability {}\n'.format(i.product_uom_qty ,i.reserved_availability)
                        Zum+=i.product_uom_qty -i.reserved_availability
                    sum_all_reserved = Zum
                except:
                    sum_all_reserved = 0
                    if self.user_has_groups('base.group_no_one'):
                        raise UserError(_(msg + "\nBy Debug mode [Sarawut Ph.] {}".format(datetime.now())))
                # sum_all_reserved = obj.move_ids.product_uom_qty - obj.move_ids.reserved_availability
                # print('sum_all_reserved', sum_all_reserved)

                if sum_all_reserved > 0:

                    mr_id = obj.env['manufacturing.request.custom'].search([('sale_order_id.order_id', '=', self.name),('state','!=','cancel')])
                    print('mr_id',mr_id)
                    if len(mr_id)!=0:
                        continue
                    print('Reserved222', obj)
                    so_val = {
                        'custom_product_template_id': obj.product_id.id,
                        'custom_product_qty': sum_all_reserved,
                        'end_date': obj.create_date,
                        'custom_date_start_wo': obj.create_date,
                        'custom_product_uom_id': obj.product_uom.id,
                        'custom_bom_id': obj.product_id.bom_ids[0].id,
                        'sale_order_id': obj.id
                        # 'custom_bom_idh': obj.product_id.variant_bom_ids.id,

                    }
                    print('so_val', so_val)
                    obj.env['manufacturing.request.custom'].create(so_val)

    def action_check_delivery(self):
        # for obj in self:
        #     print(obj)
        #     self.order_line._validate_analytic_distribution()
        #
        #     for order in self:
        #         print('aaaaaaa')
        #         order.validate_taxes_on_sales_order()
        #         if order.partner_id in order.message_partner_ids:
        #             continue
        #         order.message_subscribe([order.partner_id.id])
        #
        #     self.write(self._prepare_confirmation_values())
        #
        #     # Context key 'default_name' is sometimes propagated up to here.
        #     # We don't need it and it creates issues in the creation of linked records.
        #     context = self._context.copy()
        #     context.pop('default_name', None)
        #
        #     self.with_context(context)._action_confirm()
        #
        #
        #     obj.write({'state': 'check_delivery'})
        #
        #     for obj in self.order_line:
        #         # product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
        #         # print('product_quant',product_quant)
        #         print('objjjjjj', obj.product_uom_qty)
        #         print('objjjjjj6666', obj.move_ids)
        #         print('objjjjjj', obj.move_ids.product_virtual_available)
        #         print('objjjjjj', obj.move_ids.product_qty_available)
        #         if not obj.product_id.bom_ids:
        #             raise ValidationError(_("product รายการนี้ยังไม่มี BOM"))
        #
        #
        #         sum_all_reserved = obj.move_ids.product_uom_qty - obj.move_ids.reserved_availability
        #         print('sum_all_reserved', sum_all_reserved)
        #
        #         if sum_all_reserved > 0:
        #
        #             mr_id = obj.env['manufacturing.request.custom'].search([('sale_order_id.order_id','=',obj.name)])
        #             print('mr_id',mr_id)
        #             if mr_id:
        #                 continue
        #             print('Reserved222', obj)
        #             so_val = {
        #                 'custom_product_template_id': obj.product_id.id,
        #                 'custom_product_qty': sum_all_reserved,
        #                 'end_date': obj.create_date,
        #                 'custom_date_start_wo': obj.create_date,
        #                 'custom_product_uom_id': obj.product_uom.id,
        #                 'custom_bom_id': obj.product_id.bom_ids[0].id,
        #                 'sale_order_id': obj.id
        #                 # 'custom_bom_idh': obj.product_id.variant_bom_ids.id,
        #
        #             }
        #             print('so_val', so_val)
        #             obj.env['manufacturing.request.custom'].create(so_val)
        for res in self:
            # res.write({'state': 'sent'})
            res.write({'state': 'check_delivery'})

            for obj in self.order_line:
                if not obj.product_id.bom_ids:
                    raise ValidationError(_("product รายการนี้ยังไม่มี BOM"))


                # sum_all_reserved = obj.move_ids.product_uom_qty - obj.move_ids.reserved_availability
                # print('sum_all_reserved', sum_all_reserved)
                msg = "Err!"
                Zum = 0

                try:
                    msg += 'obj.move_ids {}\n'.format(obj.move_ids.ids)
                    for i in obj.move_ids:
                        msg += 'product_uom_qty {} reserved_availability {}\n'.format(i.product_uom_qty,
                                                                                      i.reserved_availability)
                        Zum += i.product_uom_qty - i.reserved_availability
                    sum_all_reserved = Zum
                except:
                    sum_all_reserved = 0
                    if self.user_has_groups('base.group_no_one'):
                        raise UserError(_(msg + "\nBy Debug mode [Sarawut Ph.] {}".format(datetime.now())))

                if sum_all_reserved > 0:
                    mr_id = obj.env['manufacturing.request.custom'].search([('sale_order_id.order_id','=',obj.name)])
                    print('mr_id',mr_id)
                    if mr_id:
                        continue
                    print('Reserved222', obj)
                    # so_val = {
                    #     'custom_product_template_id': obj.product_id.id,
                    #     'custom_product_qty': sum_all_reserved,
                    #     'end_date': obj.create_date,
                    #     'custom_date_start_wo': obj.create_date,
                    #     'custom_product_uom_id': obj.product_uom.id,
                    #     'custom_bom_id': obj.product_id.bom_ids[0].id,
                    #     'sale_order_id': obj.id
                    #     # 'custom_bom_idh': obj.product_id.variant_bom_ids.id,
                    # }
                    # res.mrp_production_ids.update(so_val)
                    arr = [['custom_product_template_id', obj.product_id.id],
                           ['custom_product_qty', sum_all_reserved],
                           ['end_date', obj.create_date],
                           ['custom_date_start_wo', obj.create_date],
                           ['custom_product_uom_id', obj.product_uom.id],
                           ['custom_bom_id', obj.product_id.bom_ids[0].id],
                           ['sale_order_id', obj.id],
                           ]
                    for i in arr:
                        mr = res.env['manufacturing.request.custom'].search([('sale_order_id.order_id.id','=',self.id)])
                        try:
                            mr.update({i[0]:i[1]})
                        except Exception as err:
                            if self.user_has_groups('base.group_no_one'):
                                raise UserError(_("Err {}".format(err)))
                            print("Err {}".format(err))


    def action_delivery_confirm(self):
        for obj in self:
            print(obj)
            obj.write({'state': 'delivery_confirm'})

    def action_pp_confirm(self):
        for obj in self:
            print(obj)
            obj.write({'state': 'pp_confirm',
                       # 'delivery_date': self.commitment_date
                       })

    # #
    def action_confirm_sale(self):
        print('action_confirm_sale')
        for obj in self:
            obj.write({'state': 'sale'})


    def action_set_pre_production(self):
        for obj in self:
            obj.write({'state': 'draft'})

            reset_mr_id = obj.env['manufacturing.request.custom'].search([('sale_order_id.order_id', '=', self.name),('state','!=','cancel')],
                                                                    limit=1)
            print('reset_mr_id',reset_mr_id)
            if reset_mr_id:
                mr_val = {
                    'state': 'cancel',
                }

                reset_mr_id.update(mr_val)
            for pi in obj.picking_ids:
                pi.action_cancel()








    def action_set_check_delivery(self):
        for obj in self:
            obj.write({'state': 'check_delivery'})


    def action_set_sales_order(self):
        print('action_confirm_sale')
        for obj in self:
            obj.write({'state': 'sale'})




    # def _get_forbidden_state_confirm(self):
    #     return {'done', 'cancel'}
    def action_production(self):
        for obj in self:
            print('obj')
            obj.write({'state': 'production'})
            reset_mr_id = obj.env['manufacturing.request.custom'].search(
                [('sale_order_id.order_id', '=', self.name), ('state', '!=', 'cancel')],
                )
            for mr in reset_mr_id:
                mr.update({'state':'c_validate'})

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

    # def action_do_and_mr(self):
    #     print('action_do_and_mr')
    #     #
    #     for obj in self.order_line:
    #         # product_quant = self.env['stock.quant'].search([('product_id.id', '=', obj.product_id.id)])
    #         # print('product_quant',product_quant)
    #         print('objjjjjj',obj.product_uom_qty)
    #         print('objjjjjj6666',obj.move_ids)
    #         print('objjjjjj',obj.move_ids.product_virtual_available)
    #         print('objjjjjj',obj.move_ids.product_qty_available)
    #         if not obj.product_id.bom_ids.id:
    #             raise ValidationError(_("product รายการนี้ยังไม่มี BOM"))
    #
    #         sum_all_reserved = obj.move_ids.product_uom_qty - obj.move_ids.reserved_availability
    #         print('sum_all_reserved',sum_all_reserved)
    #
    #
    #
    #         if sum_all_reserved > 0:
    #             print('Reserved222', obj)
    #             so_val = {
    #                 'custom_product_template_id': obj.product_id.id,
    #                 'custom_product_qty': sum_all_reserved,
    #                 'end_date': obj.create_date,
    #                 'custom_date_start_wo': obj.create_date,
    #                 'custom_product_uom_id': obj.product_uom.id,
    #                 'custom_bom_id': obj.product_id.bom_ids.id,
    #                 'sale_order_id':obj.id
    #                 # 'custom_bom_idh': obj.product_id.variant_bom_ids.id,
    #
    #             }
    #             print('so_val',so_val)
    #             self.env['manufacturing.request.custom'].create(so_val)




    def action_view_mr_order(self):
        print('oooooo')
        manufacturing_request = self.mapped('mr_order_sale_ids')
        action = self.env['ir.actions.actions']._for_xml_id('manufacturing_production_request.manufacturing_production_request_action')
        if len(manufacturing_request) >= 1:
            print('ffffffffffff')
            print(manufacturing_request.ids)
            action['domain'] = [('sale_order_id', '=', manufacturing_request.ids)]

        else:
            action = {'type': 'ir.actions.act_window_close'}


        return action

    # def action_view_mr_order(self):
    #     purchase_request_ids = self.mapped('mr_order_sale_ids')
    #     # action = self.env.ref('manufacturing_production_request.manufacturing_production_request_action').read()[0]
    #     action = self.env['ir.actions.actions']._for_xml_id(
    #         'manufacturing_production_request.manufacturing_production_request_action')
    #     if len(purchase_request_ids) > 1:
    #         print('purchase_request_ids',purchase_request_ids)
    #         action['domain'] = [('sale_order_id', 'in', purchase_request_ids.ids)]
    #     elif len(purchase_request_ids) == 1:
    #         form_view = [(self.env.ref('manufacturing_production_request.manufacturing_production_request_form').sale_order_id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = purchase_request_ids.id
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #
    #
    #     return action

