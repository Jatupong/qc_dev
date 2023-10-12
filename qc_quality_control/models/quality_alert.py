# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
from datetime import datetime, timedelta, date, time


class QualityDefectInProcess(models.Model):
    _name = "quality.defect.inprocess"
    _description = "Quality Alert Defect In Process"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class QualityDefectCustomer(models.Model):
    _name = "quality.defect.customer"
    _description = "Quality Alert Defect Customer"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class QualityNCPartAction(models.Model):
    _name = "ng.part.line"
    _description = "Quality Alert NG Part Action Line"

    location_id = fields.Many2one('stock.location', string='Part keeping location')
    product_qty = fields.Float('QTY', digits='Product Unit of Measure')
    action_plan = fields.Text('Action Plan', required=True)
    employee_section_id = fields.Many2one('hr.employee', string='Section')
    product_goods_qty = fields.Float('Goods', digits='Product Unit of Measure')
    product_ng_qty = fields.Float('NG', digits='Product Unit of Measure')
    quality_alert_id = fields.Many2one('quality.alert', string="Quality Alert Reference",
        required=True, ondelete='cascade', index=True, copy=False)


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    due_date = fields.Date(string='Due Date')
    employee_follow_up_id = fields.Many2one('hr.employee', string='FollowUp(PU)')
    employee_id = fields.Many2one('hr.employee', string='User(PP/SL)')
    employee_approved_id = fields.Many2one('hr.employee', string='Approved(QC&QA)')
    employee_issued_id = fields.Many2one('hr.employee', string='Issued(QC&QA)')
    is_info_by_email = fields.Boolean('Information by email')
    is_info_by_etc = fields.Boolean('Information by etc')
    info_by_etc = fields.Char('Information by etc')
    is_sort_cus_stock = fields.Boolean('Sorting customer stock')
    sort_cus_stock_qty = fields.Float('Sorting customer stock qty')
    sort_cus_stock_in = fields.Char('Sorting customer stock with in')
    is_return_replacement = fields.Boolean('Return replacement')
    return_replacement_qty = fields.Float('Return replacement qty')
    return_replacement_in = fields.Char('Return replacement in')
    is_issue_credit_note = fields.Boolean('Issue "Credit Note"')
    issue_cn_sign = fields.Char('Account sign')
    is_req_support_info_only = fields.Boolean('Information only')
    is_req_support_reply_only = fields.Boolean('Reply only')
    problem_no = fields.Char('Problem No.')
    is_ncr = fields.Boolean('NCR')
    is_car = fields.Boolean('CAR')
    mo_date_planned_start = fields.Datetime('Scheduled Start Date')
    operator_relate = fields.Char('Operator')
    name_report = fields.Char('Name of person reported')
    image_report = fields.Binary(string='Image Report')

    # Page Problem description
    production_id = fields.Many2one('mrp.production', string='Production Order')
    production_qty = fields.Float('Production Qty')
    production_check_qty = fields.Float('Production Check Qty')
    production_ng_qty = fields.Float('Production NG Qty')
    # defect detect
    is_defect_incoming = fields.Boolean('Incoming')
    is_defect_inprocess = fields.Boolean('In process')
    defect_inprocess_id = fields.Many2one('mrp.workcenter', string='In process detail')
    is_defect_out_going = fields.Boolean('Out going')
    is_defect_customer = fields.Boolean('Customer')
    defect_customer_id = fields.Many2one('res.users', string='Customer detail')
    is_defect_other = fields.Boolean('Other')
    defect_other = fields.Char('Other')

    # Page NG Part Action
    ng_part_line = fields.One2many('ng.part.line', 'quality_alert_id', string='NG Action line', copy=False, auto_join=True)
    ng_part_qty = fields.Float('NG Part Qty', digits='Product Unit of Measure', compute='_compute_ng_part_qty')
    product_goods_qty = fields.Float('Goods', digits='Product Unit of Measure', compute='_compute_ng_part_qty')
    product_ng_qty = fields.Float('NG', digits='Product Unit of Measure', compute='_compute_ng_part_qty')

    # Page Quality Tmpact
    product_part_ids = fields.Many2many('product.product', 'quality_alert_product_ref', string='Product Part')
    employee_issued_id = fields.Many2one('hr.employee', string='Issued')
    issued_date = fields.Date('Issued Date')
    employee_approve_part_id = fields.Many2one('hr.employee', string='Approved by Manager Part')
    approve_part_date = fields.Date(string='Approved by Manager Part Date')

    # QC & QA Follow up
    follow_up_note = fields.Text('Follow up note')
    result_follow = fields.Selection([('accept', 'Accept'), ('reject', 'Reject')], string='Result Follow')
    employee_qc_follow_up_id = fields.Many2one('hr.employee', string='Follow up by')
    follow_up_date = fields.Date('Follow up by')
    employee_approve_manager_id = fields.Many2one('hr.employee', string='Approved by Manager QC&QA')
    approve_part_date = fields.Date(string='Approved by Manager QC&QA Date')

    def default_get(self, fields_list):
        res = super(QualityAlert, self).default_get(fields_list)
        print('fields_list', fields_list)
        print('res', res)
        if res.get('production_id'):
            production_id = self.env['mrp.production'].browse(res.get('production_id'))
            res.update({'production_qty': production_id.product_qty,
                        'mo_date_planned_start': production_id.date_planned_start,
                        })
            print('production_id', production_id)
        if res.get('workorder_id'):
            workorder_id = self.env['mrp.workorder'].browse(res.get('workorder_id'))
            if workorder_id.state in ['progress']:
                res.update({'is_defect_inprocess': True,
                            'defect_inprocess_id': workorder_id.workcenter_id.id,
                            })
        print('res', res)
        return res

    @api.depends('ng_part_line.product_goods_qty', 'ng_part_line.product_ng_qty')
    def _compute_ng_part_qty(self):
        for obj in self:
            obj.ng_part_qty = sum(obj.ng_part_line.mapped('product_qty'))
            obj.product_goods_qty = sum(obj.ng_part_line.mapped('product_goods_qty'))
            obj.product_ng_qty = sum(obj.ng_part_line.mapped('product_ng_qty'))

