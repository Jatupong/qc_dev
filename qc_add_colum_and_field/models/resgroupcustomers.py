from odoo import api, fields, models, _


class ResGroupCustomers(models.Model):
    _name = 'res.group.customers'

    name = fields.Char('Name', required=True)