from odoo import _, api, exceptions, fields, models

class LoadingType(models.Model):
    _name = "loading.type"

    name = fields.Char(string="Name")