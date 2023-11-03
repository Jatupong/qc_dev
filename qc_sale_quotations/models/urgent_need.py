from odoo import _, api, exceptions, fields, models

class UrgentNeed(models.Model):
    _name = "urgent.need"

    name = fields.Char(string="Name")