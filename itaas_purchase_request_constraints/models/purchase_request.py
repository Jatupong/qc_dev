# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import api,fields, models, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    def make_purchase_order(self):
        print('make_purchase_order_Custom')

        over_pr = self.item_ids.filtered(lambda l: l.line_id.purchase_state
                                         and l.line_id.purchase_state != 'cancel'
                                         and l.line_id.product_qty == l.line_id.purchased_qty)
        print('over_pr',over_pr)


        print('item_ids :',self.item_ids)
        for iii in self.item_ids:
            print('iii',iii)
            print('iii',iii.line_id)
            print('iii',iii.line_id.product_qty)
            print('iii',iii.line_id.purchased_qty)
            print('kkkkk',iii.product_qty)

            data_1 = iii.line_id.product_qty
            data_2 = iii.line_id.purchased_qty
            data_3 = iii.product_qty

            sum_data = data_3 + data_2

            if sum_data > data_1:
                raise UserError(_("Not allowed to create Draft PO more than PR"))


        # purchase_request = over_pr.mapped('request_id').filtered(lambda l: not l.purchase_request_type)
        # print('purchase_request:',purchase_request)
        # if purchase_request:
        #     raise UserError(_("Please Set Purchase Request Types. \n"
        #                       "**Purchase Request Id >  %s" % purchase_request.ids))

        if over_pr:
            print('over_pr____')
            raise UserError(_("Not allowed to create Draft PO more than PR"))
            
        under_pr = self.item_ids.filtered(lambda l: l.line_id.purchase_state
                                          and l.line_id.purchase_state != 'cancel'
                                          and l.line_id.purchased_qty > l.line_id.product_qty)
        print('under_pr')


        if under_pr:
            print('under_pr____')
            raise UserError(_("Not allowed to create Draft PO more than PR"))




        return super().make_purchase_order()


