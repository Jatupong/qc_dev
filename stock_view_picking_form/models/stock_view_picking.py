# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.request"

    vin_id = fields.Char(string='หมายเลขตัวถัง (VIN No.)')

