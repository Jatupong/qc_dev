from odoo import _, api, exceptions, fields, models

class Importance(models.Model):
    _name = "importance.id"

    name = fields.Char(string="Name")