from odoo import _, api, exceptions, fields, models

class Department(models.Model):
    _name = "department.id"

    name = fields.Char(string="Name")