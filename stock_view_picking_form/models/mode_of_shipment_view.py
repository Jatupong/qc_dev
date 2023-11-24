from odoo import _, api, exceptions, fields, models

class Modeofshipment(models.Model):
    _name = "mode.shipment"

    name = fields.Char(string="Name")