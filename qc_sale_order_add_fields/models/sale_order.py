# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fob = fields.Char(string='FOB')
    incoterm = fields.Many2one(comodel_name="account.incoterms", string="Incoterm", default=lambda self: self.env.company.incoterm_id)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    shipping_mark = fields.Char(string='Shipping Mark')
    delivery_to = fields.Char(string='Delivery To')
    logo = fields.Char(string='Logo')
    delivery_week = fields.Date(string='Delivery Week Date')
    delivery_week_year = fields.Char(string='Delivery Week')

