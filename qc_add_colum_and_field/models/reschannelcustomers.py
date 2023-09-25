from odoo import api, fields, models, _


class ResChannelCustomers(models.Model):
    _name = 'res.channel.customers'

    name = fields.Char('Name', required=True)