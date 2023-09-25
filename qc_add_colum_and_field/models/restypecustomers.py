from odoo import api, fields, models, _


class ResTypeCustomers(models.Model):
    _name = 'res.type.customers'

    name = fields.Char('Name', required=True)
