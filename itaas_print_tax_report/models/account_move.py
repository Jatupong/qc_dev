# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _

class Account_journal(models.Model):
    _inherit = 'account.move'

    is_check_not_vat = fields.Boolean('Is Check Not Vat')

    @api.onchange("invoice_line_ids")
    def onchange_invoice_line_ids(self):
        tax_false = self.invoice_line_ids.filtered(lambda x: x.tax_ids.tax_report == False)
        print('invoice_line_ids:',self.invoice_line_ids)
        if tax_false:
            self.is_check_not_vat = False


