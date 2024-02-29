# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import math
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError


class account_move(models.Model):
    _inherit = "account.move"


    ####### Additional field for Invoice - JA - 20/07/2020 ############
    tax_inv_generated = fields.Boolean(string='Tax Invoice Generated',copy=False)
    tax_invoice_date = fields.Date(string='Tax Invoice Date',copy=False)
    tax_inv_number = fields.Char(string='Tax Invoice Number',copy=False)
    ref_new = fields.Char(string='อ้างอิง' ,copy=False)
    adjust_move_id = fields.Many2one('account.move', string="Tax Journal Entry", copy=False)


    ####### Additional field for Invoice - JA - 20/07/2020 ############
    #remove by JA  26/11/2022 #
    # invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
    #                            states={'draft': [('readonly', False)]})



    ######################To Manage cheque payment both account.move and account.payment #####
    # this is new bank list from res.bank
    is_create_cheque = fields.Boolean(string='Manual Cheque')
    cheque_bank = fields.Many2one('res.bank', string="ธนาคาร")
    cheque_branch = fields.Char(string="สาขา")
    cheque_number = fields.Char(string="หมายเลขเช็ค")
    cheque_date = fields.Date(string="วันที่เช็ค")
    cheque_type = fields.Selection([('paid','เช็คจ่าย'),('receive','เช็ครับ'),('transfer','โอน')], string='ประเภทเช็ค')

    ######################To Manage cheque payment both account.move and account.payment #####

    ########additional field#########
    # department_id = fields.Many2one('hr.department', string="แผนก")
    is_manual_partner = fields.Boolean(string='Partner Manual')
    supplier_name_text = fields.Char('Partner Name')
    supplier_address_text = fields.Char('Partner Address')
    supplier_branch_text = fields.Integer('Partner Branch')
    supplier_taxid_text = fields.Char('Tax ID')


    ##additional field for CN reference by JA 08/08/2021
    is_manual_cn = fields.Boolean(string='Manual CN/DN',default=False,copy=False)
    inv_ref = fields.Char('Inv Ref',copy=False)
    inv_amount_untaxed = fields.Float('Inv Untaxed Amount',copy=False)
    inv_reference_date = fields.Date(string='Inv Reference Date',copy=False)

    #additional for document management
    credit_note_reason = fields.Many2one('credit.note.reason', string='Credit/Debit Note Reason')

    #for bill to function
    bill_to_id = fields.Many2one('res.partner', string='Bill to')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        print('========================')
        self.bill_to_id = self.partner_id.bill_to_id


    def action_create_cheque(self):
        print('create_cheque')

        if self.cheque_type == 'paid':
            cheque_type = 'pay'
        elif self.cheque_type == 'receive':
            cheque_type = 'rec'

        cheque = self.line_ids.filtered(lambda x: x.account_id.is_cheque == True)
        if len(cheque) > 1:
            raise ValidationError('Warning 030: Only one cheque can be create')
        # print('Cheque:', cheque)
        if cheque:
            val = {
                'amount': cheque.debit or cheque.credit or '',
                'partner_id': cheque.partner_id.id or '',
                'account_id': cheque.account_id.id or '',
                'cheque_bank': self.cheque_bank.id or '',
                'cheque_branch': self.cheque_branch or '',
                'cheque_number': self.cheque_number or '',
                'cheque_date': self.cheque_date or '',
                'issue_date': date.today() or '',
                'move_id': self.id or '',
                'type': cheque_type or '',
                'journal_id': self.journal_id.id or ''
            }
            # print('val:', val)
            existing_cheque_id = self.env['account.cheque.statement'].search([('cheque_number','=',self.cheque_number)],limit=1)
            print (existing_cheque_id)
            if existing_cheque_id:
                raise UserError(_("Warning 031 : Cheque already exist"))
            else:
                self.env['account.cheque.statement'].create(val)
        else:
            raise UserError(_("Warning 032 : Please assign line with account for Cheque"))

    def action_gen_wht(self):
        print ('self name',self.id)
        for line in self.line_ids:
            print ('AML',line.name)
            print ('line.account_id',line.account_id.name)
            print('line.account_id', line.wht_type)

        line_ids = self.line_ids.filtered(lambda m: m.wht_type)
        print('line_ids',line_ids)
        if line_ids:
            print('action_gen_wht')
            print('contextxxxxxxxxxxxxxxxxxx', self._context)
            print('==========================')
            print(self.env.context.get('active_model'))
            print(self.env.context)
            print('===========================')
            default_type = self._context.get('active_model')
            print('default_type:', default_type)
            wht_type = line_ids.mapped('wht_type')
            print('wht_type:',wht_type)
            for wht_t in wht_type:
                wht_line_ids = line_ids.filtered(lambda m: m.wht_type == wht_t)
                if wht_line_ids:
                    wht_reference = ""

                    company_id = self.env.company
                    print('company_id:',company_id)
                    if wht_line_ids.wht_type.name == 'company':
                        print('COMPANY')
                        # sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht53.no'),('company_id','=',company_id.id)])
                        sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht53.no')])
                    elif wht_line_ids.wht_type.is_wht_2 == True:
                        print('COMPANY PND@')
                        # sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht2.no'),('company_id','=',company_id.id)])
                        sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht2.no')])
                    else:
                        print('COMPANY PND3')
                        # sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht3.no'),('company_id','=',company_id.id)])
                        sequence_id = self.env['ir.sequence'].search([('code', '=', 'wht3.no')])
                    print('sequence_id:',sequence_id)
                    if sequence_id:

                        # wht_reference = sequence_id.next_by_id()
                        if default_type == None:
                            if self.tax_invoice_date:
                                date = self.tax_invoice_date
                            else:
                                date = wht_line_ids[0].date
                            wht_reference = sequence_id.with_context(ir_sequence_date=date).next_by_id()
                            print('wht_reference:',wht_reference)
                        elif default_type == 'account.move':
                            date = wht_line_ids[0].date
                            wht_reference = sequence_id.with_context(ir_sequence_date=date).next_by_id()
                        else:
                            wht_reference = sequence_id.next_by_id()

                    for wht_l in wht_line_ids:
                        wht_l.update({
                            'wht_reference': wht_reference,
                            'wht_no': wht_reference,
                        })
    def action_post(self):
        res = super(account_move, self).action_post()
        print('action_post:')
        self.action_gen_wht()

        return res

    @api.model
    def create(self, vals):
        res = super(account_move, self).create(vals)
        print ('Create with super',vals)

        for line in res.line_ids:
            print ('LINE OF MOVE with Super')
            print ('line account',line.account_id)
            line.ref = res.ref
        return res

    @api.onchange('ref')
    def onchange_ref(self):
        for line in self.line_ids:
            line.ref = self.ref


    def roundup(self,x):
        return int(math.ceil(x / 10.0)) * 6


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = 'is_debit desc, date desc, id desc'

    wht_tax = fields.Many2one('account.tax', string="WHT", copy=False)
    wht_type = fields.Many2one('account.wht.type',string='WHT Type',)
    wht_reference = fields.Char(string="WHT Reference")

    ref = fields.Char(string="Ref" ,related=False,)
    invoice_date = fields.Date(string='Invoice/Bill Date',related='move_id.invoice_date',store=True)

    amount_before_tax = fields.Float(string='Amt Before Tax')
    wht_no = fields.Char(string="WHT No")

    is_debit = fields.Boolean(string='Is Debit', compute='get_is_debit_credit', store=True)

    @api.depends('debit', 'credit')
    def get_is_debit_credit(self):
        for line in self:
            if line.debit:
                line.is_debit = True
            else:
                line.is_debit = False


    def roundup(self,x):
        return int(math.ceil(x / 10.0)) * 10

    def roundupto(self,x):
        return int(math.ceil(x / 7.0)) * 7




class credit_note_reason(models.Model):
    _name = 'credit.note.reason'

    name = fields.Char(string='Reason')

