# -*- coding: utf-8 -*-
#Create 2024 ITAAS (Dev Sarawut Ph.)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_mr_number(self,name):

        mr_ids = self.env["manufacturing.request.custom"].search([("sale_order_id.order_id",'=', name)])
        if mr_ids:
            if len(mr_ids) == 1:
                return mr_ids.number
            else:
                msg = ""
                for i in mr_ids:
                    msg = msg+i.number+'\n'
                return msg
        else:
            return ""