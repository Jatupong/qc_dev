# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models


class StockViewPicking(models.Model):
    _inherit = "stock.picking"


    buyer_ref = fields.Char(string='Buyer REF')
    paymentref_no = fields.Char(string='Paymentref NO')

    product_ceg_th = fields.Char(string='Product Category TH')

    mode_of_shipment = fields.Many2one(comodel_name="mode.shipment", string="Mode Of Shipment")
    shipping = fields.Many2one(comodel_name="shipping.id", string="Shipping")



class StockMove(models.Model):
    _inherit = "stock.move"

    g_w_kgs_inven = fields.Char(string='G.W. KGS.')
    n_w_kgs_inven = fields.Char(string='N.W. KGS.')
