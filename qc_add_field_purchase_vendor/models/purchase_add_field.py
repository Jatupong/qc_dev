# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import tempfile
import binascii
from datetime import datetime, date
import xlrd

from odoo import fields, models, _
from odoo.exceptions import UserError
from io import BytesIO
import xlsxwriter
from dateutil.relativedelta import relativedelta

# from datetime import date

class purchase_add_field(models.Model):
    # _name = "res.partner"
    _inherit = "res.partner"

    # title = fields.Many2one('res.partner.title',string='Title',compute='_compute_title',readonly=False,store=True, required=True)
    # 
    # property_supplier_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
    #                                            string='Payment Terms',
    #                                            domain="[('company_id', 'in', [current_company_id, False])]",
    #                                            help="This payment term will be used instead of the default one for sales orders and customer invoices",
    #                                            required = True,
    #                                            )
    # vat = fields.Char(string='TAX ID',
    #                   required = True,
    #                   )
    # ref = fields.Char(string='Reference',
    #                   required=True,
    #                   )
    # street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True, required=True)
    
    # -----------------------------------------------------------------------------------------------------------------
    
    # street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True, required=True)
    # zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True, required=True)
    # city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True, required=True)

class product_template_view(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(string='Internal Reference', required=True)
