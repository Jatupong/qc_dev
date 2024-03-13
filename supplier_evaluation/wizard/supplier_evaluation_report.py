# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from datetime import datetime
from odoo import tools
# from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo import api, models, fields, _
import xlwt
import time
import xlsxwriter
import base64
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.tools import misc
import operator
import locale
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import calendar

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class wizard_suplier_evaluation(models.TransientModel):
    _name = 'wizard.suplier.evaluation'

    evaluation_report_type = fields.Selection([('date', 'Date'), ('year', 'Year'),], string='Type', default='date',)
    year = fields.Char(string='Year')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total_supplier_ids = fields.Many2many('res.partner','total_supplier_ids', string='Total Partner',store=True)
    partner_ids = fields.Many2many('res.partner','partner_ids', string='Partner', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    evaluate_by = fields.Many2one('res.users', string='Evaluate By', default=lambda self: self.env.uid)
    evaluate_date = fields.Date(string="Evaluate Date", default=fields.Date.today())
    validate_by = fields.Many2one('res.users', string='Validate By', default=lambda self: self.env.uid)

    @api.onchange('year')
    def _get_total_supplier(self):
        for odj in self:
            year = odj.year
            try:
                year_int = int(year)
            except ValueError:
                raise UserError(_('Please Check Year!'))
            date_from = str(year) + '-01-01'
            date_to = str(year) + '-12-31'
            evaluation_ids = odj.env['supplier.evaluation'].search([('date', '>=', date_from), ('date', '<=', date_to)])
            supplier_ids = []
            partner_evaluation_ids = evaluation_ids.mapped('partner_id')
            if partner_evaluation_ids:
                for partner in partner_evaluation_ids:
                    if partner.id not in supplier_ids:
                        supplier_ids.append(partner.id)
                odj.update({
                    'total_supplier_ids': [(6, 0, supplier_ids)],
                })

    @api.model
    def default_get(self, fields):
        res = super(wizard_suplier_evaluation, self).default_get(fields)
        curr_date = datetime.now()
        year = str(curr_date.year)

        from_date = datetime(curr_date.year, 1, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date),'year':year,})
        return res

    def print_pdf_report(self, data):
        print("print_pdf_report summary_supplier_evaluation")
        data = {}
        data['form'] = self.read(['year','date_from', 'date_to', 'partner_ids', 'company_id','from_no','to_no'])[0]
        return self.env.ref('supplier_evaluation.summary_supplier_evaluation').report_action(self, data=data,config=False)

    def get_score_vender(self,partner,year):
        # print('get_score_vender')
        year = year
        evaluation = []
        val = {}
        # 4 part
        for q in range(0,4,1):
            if q == 0:
                date_from = year + '-01-01'
                date_to = year + '-03-30'
            elif q == 1:
                date_from = year + '-04-01'
                date_to = year + '-06-30'
            elif q == 2:
                date_from = year + '-07-01'
                date_to = year + '-09-30'
            else:
                date_from = year + '-08-01'
                date_to = year + '-12-31'

            evaluation_ids = self.env['supplier.evaluation'].sudo().search([('partner_id', '>=', partner.id),
                                                                            ('date', '>=', date_from), ('date', '<=', date_to)])
            if evaluation_ids:
                evaluation_type = self.env['evaluation.type'].sudo().search([])
                percent_score_total = 0
                for line in evaluation_ids.filtered(lambda x: x.evaluation_line_ids):
                    for line_in in line.evaluation_line_ids:
                        result_score = score = total_score = 0
                        for type in evaluation_type:
                            evaluation_name = self.env['evaluation.name'].sudo().search([('type_id','=',type.id)])
                            for name in evaluation_name:
                                score += name.score
                                data = line.get_evaluation_data(line,name)
                                if data:
                                    result_score += data.result_score
                                else:
                                    result_score += name.score
                                total_score += result_score
                    percent_score = (result_score / score) * 100
                    percent_score_total = percent_score_total + percent_score
                evaluation_len = len(evaluation_ids)
                quarter_percent_score = percent_score_total / evaluation_len
                evaluation.append({'quarter':q+1,'percent_score':quarter_percent_score,'total_score':total_score,'has_data':True})
            else:
                evaluation.append({'quarter':q+1,'percent_score': 0,'total_score':0,'has_data':False})
        return evaluation


class summary_supplier_evaluation_report(models.AbstractModel):
    _name = 'report.supplier_evaluation.summary_supplier_evaluation_id'

    # @api.multi
    def get_report_values(self, docids, data=None):
        print ('def get_report_values')
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        doc_model = 'supplier.evaluation'
        domain = []
        if data:
            data = data
            if data['form']['year']:
                year = data['form']['year']
                try:
                    year_int = int(year)
                except ValueError:
                    raise UserError(_('Please Check Year!'))
                date_from = str(year) + '-01-01'
                date_to = str(year) + '-12-31'
                domain.append(('date', '>=', date_from))
                domain.append(('date', '<=', date_to))
            if data['form']['partner_ids']:
                partner_ids = data['form']['partner_ids']
                # print(data['form']['partner_ids'])
                domain.append(('partner_id', 'in', partner_ids))
        evaluation_ids = self.env['supplier.evaluation'].search(domain)
        if not evaluation_ids:
            raise UserError(_('There is record this date range.'))

        supplier_ids = []
        for es in evaluation_ids:
            if es.partner_id not in supplier_ids:
                supplier_ids.append(es.partner_id)

        docargs = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'data': data['form'],
            'docs': docs,
            'supplier_ids': supplier_ids,
            'year': str(year),
            'date_from': date_from,
            'date_to': date_to,
        }
        return docargs