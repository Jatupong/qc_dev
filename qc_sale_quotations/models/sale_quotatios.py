# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.

from odoo import api, fields, models, _


class SaleQuotation(models.Model):
    _inherit = 'sale.order'

    department = fields.Many2one(comodel_name='department.id', string='แผนก',store=False,)
    id_pp = fields.Char(string='PP No.')
    id_po = fields.Char(string='PO No.')
    w_load_product = fields.Char(string='Requested Week')
    box_type = fields.Many2one(comodel_name='box.type' ,string='Packaging')
    download_with = fields.Char(string='Consolidate With')


    correction = fields.Char(string='Revision')
    # currency = fields.Many2one(comodel_name='res.currency', string='Currency', store=False)
    currency = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    container = fields.Char(string='Container Size')
    loading_type = fields.Many2one(comodel_name='loading.type', string='Loading Type')
    bar_code = fields.Char(string='BarCode')


    urgent_need = fields.Many2one(comodel_name='urgent.need', string='Urgent Need')
    want_to_deliver = fields.Many2one(comodel_name='want.to.deliver', string='Want To Deliver')
    Importance = fields.Many2one(comodel_name='importance.id', string='Importance')
    important_note = fields.Text(string='Important Note')

    special_need = fields.One2many('sale.quotation.lines', 'sale_quotation_id', string='ความต้องการพิเศษ')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Detail')


class SaleQuotationLines(models.Model):
    _name = 'sale.quotation.lines'
    _description = 'Sale Quotation Lines'

    sale_quotation_id = fields.Many2one('sale.order', string='Sale Quotation')
    # กำหนดฟิลด์ที่คุณต้องการในคลาสนี้
    Description = fields.Char(string='Description')
    # field_name_2 = fields.Char(string='Field Name 2')