# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
# from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class supplier_evaluation(models.Model):
    _name = 'supplier.evaluation'
    _inherit = 'mail.thread'
    _order = 'date desc'

    date = fields.Date(string='Date', required=True ,default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    po_id = fields.Many2one('purchase.order', string='PO')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    # ------------------------------------------------------------------------------------------------------------------
    evaluation_line_ids = fields.One2many('supplier.evaluation.line', 'supplier_evaluation_id', string='Evaluation')
    score_total = fields.Integer(string='Score Total', store=True, readonly=True, compute='_score_all',track_visibility='onchange')
    deduct_score_total = fields.Integer(string='Deduct Total', store=True, readonly=True, compute='_score_all', track_visibility='onchange')
    result_score_total = fields.Integer(string='Result Score Total', store=True, readonly=True, compute='_score_all', track_visibility='onchange')
    score_grade = fields.Many2one('score.grade', String="Grade", store=True, readonly=True, compute='_score_all', track_visibility='onchange')
    # ------------------------------------------------------------------------------------------------------------------
    objective = fields.Selection([('new_vendor', 'ผู้ผลิตรายใหม่/New Vendor'),('process', 'ผลิตภัณฑ์ใหม่/Process Change'),
        ('annual', 'ตรวจประเมินประจำปี/Annual Audit'),],string='Objective',default='new_vendor')
    type_partner = fields.Selection([('vendor', 'ผู้ขาย/ผู้ผลิต/Vendor'),('outsource', 'ผู้รับจ้างช่วง/Outsource'),],string='Type Partner',default='vendor')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    # ------------------------------------------------------------------------------------------------------------------
    contact_person = fields.Many2many('res.partner', string='Contact Person', domain="[('parent_id', '=', partner_id)]")
    auditor_ids = fields.Many2many('res.users', string='Auditor')
    standard_iso = fields.Char('ISO')
    standard_as_ie = fields.Char('AS / IE')
    standard_other = fields.Char('Other')

    @api.model
    def default_get(self, flds):
        result = super(supplier_evaluation, self).default_get(flds)
        users = []
        users.append(self.env.uid)
        result['auditor_ids'] = users
        return result

    @api.depends('date','partner_id')
    def name_get(self):
        result = []
        for line in self:
            partner = line.partner_id.name
            date = line.date
            name = "[" + str(date) + "]" + str(partner)
            result.append((line.id, name))
        return result

    @api.depends('evaluation_line_ids.deduct_score')
    def _score_all(self):
        for order in self:
            deduct_score_total = score_total = result_score_total = 0
            score_total = sum(self.env['evaluation.name'].sudo().search([]).mapped('score'))
            for line in order.evaluation_line_ids:
                deduct_score_total += line.deduct_score
            result_score_total = score_total - deduct_score_total
            if result_score_total != 0:
                score_grade = ( result_score_total / score_total ) * 100
            elif result_score_total == 0 and score_total == 0:
                score_grade = 0
            grade = self.env['score.grade'].sudo().search([('max_score', '>=', score_grade)], limit=1,
                                                                      order='max_score asc')
            order.update({
                'score_total': score_total,
                'deduct_score_total': deduct_score_total,
                'result_score_total': result_score_total,
                'score_grade':  grade.id or False,
            })

    def get_evaluation_data(self,obj,line):
        data = obj.evaluation_line_ids.filtered(lambda x: x.type_id.id == line.type_id.id and x.name.id == line.id)
        if data:
            data = data[0]
        return data


class supplier_evaluation_line(models.Model):
    _name = 'supplier.evaluation.line'

    supplier_evaluation_id = fields.Many2one('supplier.evaluation', string='Supplier Evaluation Reference', ondelete='cascade', copy=False)
    name = fields.Many2one('evaluation.name', string='Name', required=True)
    type_id = fields.Many2one('evaluation.type', string='Type',required=True)
    score = fields.Integer(string='Score', related='name.score')
    deduct_score = fields.Integer(string='Deduction Score',required=True)
    result_score = fields.Integer(string='Score Total')
    description = fields.Char(string='Description')

    @api.onchange('deduct_score','score')
    def onchange_deduct_score(self):
        for order in self:
            if order.score < order.deduct_score:
                raise UserError(_('Shouldn\'t be more than Score'))
            else:
                order.result_score = order.score - order.deduct_score

    _sql_constraints = [('unique_type_and_name', 'unique(type_id, name, supplier_evaluation_id)',
                         'Cannot Use one type and one name!\nPlease, select a different')]


class evaluation_type(models.Model):
    _name = 'evaluation.type'
    _rec_name = 'name'
    _order = "sequence asc"

    name = fields.Text(string='Name')
    name_th = fields.Text(string='Name TH')
    sequence = fields.Integer(string='Sequence')
    description = fields.Char(string='Description')

    @api.depends('name','sequence')
    def name_get(self):
        result = []
        name = ""
        for line in self:
            if line.sequence:
                name = str(line.sequence) + "-"
            if line.name:
                name += line.name
            result.append((line.id, name))
        return result


class evaluation_name(models.Model):
    _name = 'evaluation.name'
    _rec_name = 'name'
    _order = "type_id , sequence asc"

    def _default_score(self):
        score = 0
        data_demo = self.env['score.method'].sudo().search([],limit=1)
        if data_demo:
            score = data_demo.score
        return score

    name = fields.Text(string='Name')
    name_th = fields.Text(string='Name TH')
    type_id = fields.Many2one('evaluation.type', string='Type')
    sequence = fields.Integer(string='Sequence')
    score = fields.Integer(string='Score',default=_default_score)

    @api.depends('name','sequence')
    def name_get(self):
        result = []
        name = ""
        for line in self:
            if line.sequence:
                name = str(line.sequence) + "-"
            if line.name:
                name += line.name
            result.append((line.id, name))
        return result


class ScoreMethod(models.Model):
    _name = 'score.method'
    _rec_name = 'score'
    _order = "score desc"

    score = fields.Integer(string='Score', required=True)
    name = fields.Text(string='Name')
    name_th = fields.Text(string='Name TH')

    _sql_constraints = [('score_uniq', 'unique(score)', 'Score of the Method levels must be different')]


class score_grade(models.Model):
    _name = 'score.grade'
    _rec_name = 'name'
    _order = "max_score desc"

    name = fields.Text(string='Name' ,required=True)
    min_score = fields.Integer(string='Min score' ,required=True)
    max_score = fields.Integer(string='Max score' ,required=True)
    result = fields.Selection([('pass', 'Pass'), ('not', 'Fail'), ], string='Result',default='pass',required=True)
    description = fields.Char(string='Description')

    _sql_constraints = [('min_score_uniq', 'unique(min_score)', 'Min score of the Score levels must be different'),
                        ('max_score_uniq', 'unique(max_score)', 'Max score of the Score levels must be different')]






