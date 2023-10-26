# -*- coding: utf-8 -*-
# Copyright (C) 2022 (www.itaas.co.th)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    internal_transfer_no_form = fields.Char(string='Internal Transfer No. Form')
    delivery_no_form = fields.Char(string='Delivery No. Form')
    receipt_no_form = fields.Char(string='Receipt No. Form')
    return_in_form = fields.Char(string='Return In No. Form')
    return_out_form = fields.Char(string='Return Out No. Form')
    product_delivery_note = fields.Char(string='ใบส่งมอบผลิตภัณฑ์')
    packing_list = fields.Char(string='Packing List')
    product_delivery_note_number = fields.Char(string='เลขที่แก้ไขใบส่งมอบผลิตภัณฑ์')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    internal_transfer_no_form = fields.Char(related='company_id.internal_transfer_no_form', string='Internal Transfer No. Form', readonly=False)
    delivery_no_form = fields.Char(related='company_id.delivery_no_form', string='Delivery No. Form', readonly=False)
    receipt_no_form = fields.Char(related='company_id.receipt_no_form', string='Receipt No. Form', readonly=False)
    return_in_form = fields.Char(related='company_id.return_in_form', string='Return In No. Form', readonly=False)
    return_out_form = fields.Char(related='company_id.return_out_form', string='Return Out No. Form', readonly=False)
    product_delivery_note = fields.Char(related='company_id.product_delivery_note', string='ใบส่งมอบผลิตภัณฑ์', readonly=False)
    packing_list = fields.Char(related='company_id.packing_list', string='Packing List', readonly=False)
    product_delivery_note_number = fields.Char(related='company_id.product_delivery_note_number', string='เลขที่แก้ไขใบส่งมอบผลิตภัณฑ์',
                                        readonly=False)