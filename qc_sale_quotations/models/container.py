from odoo import _, api, exceptions, fields, models

class Container(models.Model):
    _name = "container.id"

    name = fields.Char(string="Name")