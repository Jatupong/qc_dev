# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd. (www.itaas.co.th)

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    branch_no = fields.Char(string='Branch', default='00000')
    fax = fields.Char(string='Fax')
    building = fields.Char(string='Building', size=32)
    room_number = fields.Char(string='Room number', size=32)
    floor_number = fields.Char(string='Floor number', size=32)
    village = fields.Char(string='Village', size=64)
    house_number = fields.Char(string='House number', size=20)
    moo_number = fields.Char(string='Moo number', size=20)
    soi_number = fields.Char(string='Soi number', size=24)
    road = fields.Char(string='Road')
    sub_district = fields.Char(string='Sub District')
    district = fields.Char(string='District')
    province = fields.Char(string='Province')
    postcode = fields.Char(string='Postcode')
    english_name = fields.Char(string='English Name')
    english_address = fields.Char(string='English Address')

    def get_company_full_address(self):
        address = []
        # use in qweb company_address = o.company_id.get_company_full_address()
        # <t t-set="company_address" t-value="o.company_id.get_company_full_address()"/>
        # <span t-esc="' '.join([ address for address in company_address ])"/>
        if self.country_id.code == 'TH':
            if self.building:
                address.append('อาคาร' + str(self.building))
            if self.room_number:
                address.append('ห้องเลขที่' + str(self.room_number))
            if self.floor_number:
                address.append('ชั้นที่' + str(self.floor_number))
            if self.village:
                address.append('หมู่บ้าน' + str(self.village))
            if self.house_number:
                address.append('เลขที่' + str(self.house_number))
            if self.moo_number:
                address.append('หมู่ที่' + str(self.moo_number))
            if self.soi_number:
                address.append('ซอย' + str(self.soi_number))
            if self.road:
                address.append('ถนน' + str(self.road))

            if self.state_id and self.state_id.code == 'BKK':
                if self.sub_district:
                    address.append('แขวง' + str(self.sub_district))
                if self.district:
                    address.append('เขต' + str(self.district))
                address.append(str(self.state_id.name))
            elif self.state_id:
                if self.sub_district:
                    address.append('ตำบล' + str(self.sub_district))
                if self.district:
                    address.append('อำเภอ' + str(self.district))
                address.append('จังหวัด' + str(self.state_id.name))
        else:
            if self.street:
                address.append(str(self.street))
            if self.street2:
                address.append(str(self.street2))
            if self.city:
                address.append(str(self.city))
            if self.state_id:
                address.append(str(self.state_id.name))
            if self.country_id:
                address.append(str(self.country_id.name))
        if self.zip:
            address.append(str(self.zip))

        return address

    def get_company_full_address_text(self):
        address = self.get_company_full_address()
        address_text = ' '.join(address)
        return address_text

