# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, fields, models


class PurchaseRequestDepartment(models.Model):
    _inherit = "purchase.request"

    department_id_1 = fields.Many2one('hr.department',string='Department')
    assign_to = fields.Many2one('hr.employee',string='Approver')

    @api.onchange("department_id_1")
    def onchange_department_id_1(self):
        # employees = self.department_id.manager_id
        if self.department_id_1:
            self.assign_to = self.department_id_1.manager_id.id
        else: self.assign_to = False

