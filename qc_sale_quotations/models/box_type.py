from odoo import _, api, exceptions, fields, models

class Department(models.Model):
    _name = "box.type"

    name = fields.Char(string="Name")