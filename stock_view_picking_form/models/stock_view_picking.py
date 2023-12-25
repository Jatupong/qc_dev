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

    width_inven = fields.Float(string='WIDTH', related="sale_line_id.width")
    length_inven = fields.Float(string='LENGTH', related="sale_line_id.length")
    height_inven = fields.Float(string='HEIGHT', related="sale_line_id.height")
    g_w_kgs_inven = fields.Float(string='G.W. KGS.', related="sale_line_id.g_w_kgs")
    n_w_kgs_inven = fields.Float(string='N.W. KGS.', related="sale_line_id.n_w_kgs")


