from odoo import _, api, exceptions, fields, models

class WantToDeliver(models.Model):
    _name = "want.to.deliver"

    name = fields.Char(string="Name")