from odoo import _, api, exceptions, fields, models

class Shipping(models.Model):
    _name = "shipping.id"

    name = fields.Char(string="Name")