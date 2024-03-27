from odoo import _, api, exceptions, fields, models

class Container(models.Model):
    _name = "container.id"

    name = fields.Char(string="Name")




class SaleQuotation(models.Model):
    _inherit = 'sale.order'

    container_new = fields.Many2one(comodel_name='container.id', string='Container Size')

    