# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class mrp_bom(models.Model):
    _inherit ="mrp.bom"

    capacity_line_ids = fields.One2many('mrp.bom.capacity.line','bom_id',string='Capacity')



class mrp_bom_capacity_line(models.Model):
    _name ="mrp.bom.capacity.line"

    work_center_id = fields.Many2one('mrp.workcenter')
    uph = fields.Float(string='UPH')
    note = fields.Char(string='Note')
    bom_id = fields.Many2one('mrp.bom',string='BOM')



