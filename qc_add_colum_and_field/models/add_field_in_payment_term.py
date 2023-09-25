from odoo import models, fields, api


class AddFieldInPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_term_code = fields.Char(string="Payment term code",store = True)







