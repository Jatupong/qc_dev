# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today (ITAAS)

from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    branch_no = fields.Char(string='Branch',default='00000')

    #only some customer for detail of address
    building = fields.Char(string='building', size=32)
    roomnumber = fields.Char(string='roomnumber', size=32)
    floornumber = fields.Char(string='floornumber', size=32)
    village = fields.Char(string='village', size=64)
    house_number = fields.Char(string='house_number', size=20)
    moo_number = fields.Char(string='moo_number', size=20)
    soi_number = fields.Char(string='soi_number', size=24)
    road = fields.Char(string='road', size=24)
    tumbon = fields.Char(string='tumbon', size=24)
    city_new = fields.Char(string='City', size=24)
    state_id_new = fields.Many2one('res.country.state',string='City', size=24)
    english_company_name = fields.Char(string='English Name')
    english_address = fields.Char(string='English Adress')



    def get_company_account_full_address(self):
        address = ''

        if self.building:
            address = address + ' อาคาร' + str((self.building).encode('utf-8'))
        if self.roomnumber:
            address = address + ' ห้องเลขที่' + str((self.roomnumber).encode('utf-8'))
        if self.floornumber:
            address = address + ' ชั้นที่' + str((self.floornumber).encode('utf-8'))
        if self.village:
            address = address + ' หมู่บ้าน' + str((self.village).encode('utf-8'))
        if self.house_number:
            address = address + ' เลขที่' + str((self.house_number).encode('utf-8'))
        if self.moo_number:
            address = address + ' หมู่ที่' + str((self.moo_number).encode('utf-8'))
        if self.tumbon:
            address = address + ' ตำบล ' + str((self.tumbon).encode('utf-8'))
        if self.soi_number:
            address = address + ' ซอย' + str((self.soi_number).encode('utf-8'))
        if self.road:
            address = address + ' ถนน' + str((self.road).encode('utf-8'))
        if self.city_new and self.state_id_new and self.state_id_new.code != 'BKK':
            address = address + ' อำเภอ' + str((self.city_new).encode('utf-8'))
        if self.city_new and self.state_id_new and self.state_id_new.code == 'BKK':
            address = address + ' เขต' + str((self.city_new).encode('utf-8'))
        if self.state_id_new:
            address = address + ' จังหวัด' + str((self.state_id_new.name).encode('utf-8'))

        return address

    def get_company_full_address(self):
        address = ''

        if self.street:
            address = address + str((self.street).encode('utf-8'))
        if self.street2:
            address = address + str((self.street2).encode('utf-8'))
        if self.city and self.state_id and self.state_id.code != 'BKK':
            address = address + ' อำเภอ' + str((self.city).encode('utf-8'))
        if self.city and self.state_id and self.state_id.code == 'BKK':
            address = address + ' เขต' + str((self.city).encode('utf-8'))
        if self.state_id:
            address = address + ' จังหวัด' + str((self.state_id.name).encode('utf-8'))

        return address

    def get_company_full_address_text(self):
        address = self.get_company_full_address_array()
        address_text = ' '.join(address)
        return address_text

    def get_company_full_address_array(self):
        address = []
        if self.street:
            address.append(str(self.street))
        if self.street2:
            address.append(str(self.street2))
        if self.city:
            address.append(str(self.city))
        if self.state_id:
            address.append(str(self.state_id.name))
        if self.zip:
            address.append(str(self.zip))

        return address



