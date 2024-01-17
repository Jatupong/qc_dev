from odoo import _, api, exceptions, fields, models

class Department(models.Model):
    _name = "currency.id"

    name = fields.Char(string="Name")
    
    