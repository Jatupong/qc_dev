# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleQuotation(models.Model):
    _inherit = 'sale.order'

    department = fields.Many2one(comodel_name='department.id', string='แผนก',store=False,)
    id_pp = fields.Char(string='PP No.')
    id_po = fields.Char(string='PO No.')
    w_load_product = fields.Char(string='Requested Week')
    w_load_product_week = fields.Date(string='Requested Week Date')
    box_type = fields.Many2one(comodel_name='box.type' ,string='Packaging')
    download_with = fields.Char(string='Consolidate With')


    correction = fields.Char(string='Revision')
    # currency = fields.Char(string='Currency',store=False)
    currency = fields.Char(string='Currency')
    container = fields.Char(string='Container Size', invisible=True)
    # container_new = fields.Char(comodel_name='container.id', string='Container Size')
    loading_type = fields.Many2one(comodel_name='loading.type', string='Loading Type')
    bar_code = fields.Char(string='BarCode')



    urgent_need = fields.Many2one(comodel_name='urgent.need', string='Urgent Need')
    want_to_deliver = fields.Many2one(comodel_name='want.to.deliver', string='Want To Deliver')
    Importance = fields.Many2one(comodel_name='importance.id', string='Importance')
    important_note = fields.Text(string='Important Note')
    description = fields.Text(string='Description')

    special_need = fields.One2many('sale.quotation.lines', 'sale_quotation_id', string='ความต้องการพิเศษ')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Detail')

    @api.onchange('description')
    def update_description_mr(self):
        for sale in self:
            domain = [('sale_order_id.id','in',sale.mr_order_sale_ids.ids)]
            mr = sale.env['manufacturing.request.custom'].search(domain)
            msg=''
            for i in mr:
                i.update({
                    'custom_description':sale.description
                })
                msg+='mr={}\n'.format(i)
            print(msg)
            if len(mr)==0:
                raise UserError(_("description:{}\nme={}".format(sale.description,mr)))

    @api.onchange('w_load_product_week','delivery_date,','delivery_date','delivery_exp_date')
    def update_week(self):
        if self.w_load_product_week != False:
            try:
                self.update({
                    'w_load_product': "W{}".format(self.w_load_product_week.isocalendar().week)
                })
            except:
                pass
        if 'delivery_date' in self.fields_get():
            try:
                if self.delivery_date != False:
                    self.update({
                        'delivery_date_week': "W{}".format(self.delivery_date.isocalendar().week)
                    })
            except:
                pass
        if 'delivery_week' in self.fields_get():
            try:
                if self.delivery_week != False:
                    self.update({
                        'delivery_week_year': "W{}".format(self.delivery_week.isocalendar().week)
                    })
            except:
                pass
        if 'delivery_exp_date' in self.fields_get():
            if self.delivery_exp_date != False:
                try:
                    self.update({
                        'delivery_exp_week': "W{}".format(self.delivery_exp_date.isocalendar().week)
                    })
                except:
                    pass





class SaleQuotationLines(models.Model):
    _name = 'sale.quotation.lines'
    _description = 'Sale Quotation Lines'

    sale_quotation_id = fields.Many2one('sale.order', string='Sale Quotation')
    # กำหนดฟิลด์ที่คุณต้องการในคลาสนี้
    Description = fields.Char(string='Description')
    # field_name_2 = fields.Char(string='Field Name 2')