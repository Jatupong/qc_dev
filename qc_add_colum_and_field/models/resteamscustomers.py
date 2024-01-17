from odoo import api, fields, models, _


class ResTeamsCustomers(models.Model):
    _name = 'res.teams.customers'

    name = fields.Char('Name', required=True)




