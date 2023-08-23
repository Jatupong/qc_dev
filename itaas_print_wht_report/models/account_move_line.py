# © 2019 ForgeFlow S.L.
# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
from bahttext import bahttext
from datetime import datetime, timedelta
from odoo import api,fields, models, _
from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import base64
import xlwt
import math

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_num_page(self, record, max_record):
        return int(math.ceil((record / max_record)))


    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def get_onetime_move_line_to_move(self):
        for obj in self:
            address = []
            vals={
                'name':obj.move_id.name_onetime,
                'address':obj.move_id.address_onetime,
                'vat':obj.move_id.tax_onetime,
                'street':'',
                'street2':'',
                'sub_district':'',
                'district':'',
                'state':'',
                'zip':'',
                'city':'',
                'branch': '',
            }
            address.append(vals)

            return address

    def get_onetime(self):
        for move_id in self:
            address = []
            vals={
                'name':move_id.name_onetime,
                'address':move_id.address_onetime,
                'vat':move_id.tax_onetime,
                'street':'',
                'street2':'',
                'sub_district':'',
                'district':'',
                'state':'',
                'zip':'',
                'city':'',
                'branch': '',
            }
            address.append(vals)

            return address

    def get_address(self):
        print('get_address:')
        for order in self:
            print('NOT ONETIME')
            address = []
            street = ''
            street2 = ''
            sub_district = ''
            district = ''
            city = ''
            state_id = ''
            zip = ''
            partner = order.partner_id
            if partner.country_id.code == 'TH':
                if partner.street:
                    street = partner.street
                else:
                    street = ''

                if partner.street2:
                    street2 = partner.street2
                else:
                    street2 = ''
                if partner.state_id and partner.state_id.code == 'BKK':
                    if partner.sub_district_id:
                        sub_district = 'แขวง' + str(partner.sub_district_id.name)
                    if partner.district_id:
                        district = 'เขต' + str(partner.district_id.name)
                    elif partner.city:
                        city = 'เขต' + str(partner.city)
                    state_id = partner.state_id.name

                elif partner.state_id:
                    if partner.sub_district_id:
                        sub_district = 'ตำบล' + str(partner.sub_district_id.name)

                    if partner.district_id:
                        district = 'อำเภอ' + str(partner.district_id.name)
                    elif partner.city:
                        city = 'อำเภอ' + str(partner.city)
                    state_id = 'จังหวัด' + str(partner.state_id.name)
            else:

                if partner.street:
                    street = partner.street
                if partner.street2:
                    street2 = partner.street2
                if partner.city:
                    city = partner.city
                if partner.state_id:
                    state_id = partner.state_id.name
            if partner.zip:
                zip = partner.zip
            if partner.vat:
                vat = partner.vat
            else:
                vat = ''

            if partner.branch_no == '00000':
                branch = '(สำนักงานใหญ่)'
            else:
                branch = 'สาขาที่ ' + str(partner.branch_no)
            vals = {
                'name': '',
                'address': '',
                'vat': vat or '',
                'street': street,
                'street2': street2,
                'sub_district': sub_district,
                'district': district,
                'state': state_id,
                'zip': zip,
                'city': city,
                'branch':branch,
            }
            address.append(vals)
            print('address_NOT ONETIME:',address)
            return address[0]