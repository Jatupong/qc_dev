# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.

from odoo import api, fields, models, _


class SaleQuotation(models.Model):
    _inherit = 'sale.order'

    department = fields.Many2one(comodel_name='department.id', string='แผนก')
    id_pp = fields.Char(string='รหัส PP')
    id_po = fields.Char(string='รหัสPO')
    w_load_product = fields.Char(string='Wโหลดสินค้า')
    box_type = fields.Many2one(comodel_name='box.type' ,string='Box Type')
    download_with = fields.Char(string='Download With')


    correction = fields.Char(string='Correction')
    currency = fields.Char(string='Currency')
    container = fields.Char(string='Container')
    loading_type = fields.Many2one(comodel_name='loading.type', string='Loading Type')
    bar_code = fields.Char(string='Bar Code')


    urgent_need = fields.Many2one(comodel_name='urgent.need', string='Urgent Need')
    want_to_deliver = fields.Many2one(comodel_name='want.to.deliver', string='Want To Deliver')
    Importance = fields.Many2one(comodel_name='importance.id', string='Importance')
    important_note = fields.Text(string='Important Note')

    special_need = fields.One2many('sale.quotation.lines', 'sale_quotation_id', string='ความต้องการพิเศษ')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank')


class SaleQuotationLines(models.Model):
    _name = 'sale.quotation.lines'
    _description = 'Sale Quotation Lines'

    sale_quotation_id = fields.Many2one('sale.order', string='Sale Quotation')
    # กำหนดฟิลด์ที่คุณต้องการในคลาสนี้
    Description = fields.Char(string='Description')
    # field_name_2 = fields.Char(string='Field Name 2')