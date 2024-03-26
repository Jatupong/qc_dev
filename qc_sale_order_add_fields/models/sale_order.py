# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fob = fields.Char(string='FOB')
    shipping_mark = fields.Char(string='Shipping Mark')
    delivery_to = fields.Char(string='Delivery To')
    logo = fields.Char(string='Logo')
    delivery_week = fields.Date(string='Delivery Week Date')
    delivery_week_year = fields.Char(string='Delivery Week')

    @api.onchange('delivery_week')
    def update_delivery_week(self):
        for sale in self:
            if sale.delivery_week != False:
                sale.delivery_week_year = "W{}".format(sale.delivery_week.isocalendar().week)
            else:
                sale.delivery_week_year = "Week"