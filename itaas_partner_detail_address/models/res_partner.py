# -*- coding: utf-8 -*-
# Copyright (C) 2019-present  Technaureus Info Solutions Pvt.Ltd.(<http://www.technaureus.com/>).
from odoo import fields, api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    district_id = fields.Many2one('res.district', string='District')
    sub_district_id = fields.Many2one('res.sub.district', string='Sub District')
    fax = fields.Char(string='Fax')
    branch_no = fields.Char(string='Branch', default='00000')

    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self.country_id.address_format or \
                         "%(street)s\n%(street2)s\n%(sub_district_name)s %(district_name)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'sub_district_code': self.sub_district_id.code or '',
            'sub_district_name': self.sub_district_id.name or '',
            'district_code': self.district_id.code or '',
            'district_name': self.district_id.name or '',
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    def _display_address_depends(self):
        res = super(Partner, self)._display_address_depends()
        res = res + ['district_id', 'district_id.code', 'district_id.name', 'sub_district_id', 'sub_district_id.code', 'sub_district_id.name']
        return res

    @api.onchange('sub_district_id')
    def _onchange_sub_district_id(self):
        if self.sub_district_id:
            self.district_id = self.sub_district_id.district_id.id
            self.state_id = self.sub_district_id.district_id.state_id.id
            self.zip = self.sub_district_id.zip
            self.country_id = self.sub_district_id.district_id.state_id.country_id.id

    @api.depends('street', 'zip', 'city', 'country_id', 'district_id', 'sub_district_id')
    def _compute_complete_address(self):
        for record in self:
            record.contact_address_complete = ''
            if record.street:
                record.contact_address_complete += record.street+','
            if record.district_id:
                record.contact_address_complete += record.district_id.name+' '
            if record.sub_district_id:
                record.contact_address_complete += record.sub_district_id.name+' '
            if record.zip:
                record.contact_address_complete += record.zip+ ' '
            if record.city:
                record.contact_address_complete += record.city+','
            if record.country_id:
                record.contact_address_complete += record.country_id.name

    def get_partner_full_address_text(self):
        address = self.get_partner_full_address()
        address_text = ' '.join(address)
        return address_text

    def get_partner_full_address(self):
        address = []
        # use in qweb partner_address = o.partner_id.get_partner_full_address()
        # <t t-set="partner_address" t-value="o.partner_id.get_partner_full_address()"/>
        # <span t-esc="' '.join([ address for address in partner_address ])"/>
        if self.country_id.code == 'TH':
            if self.street:
                address.append(str(self.street))
            if self.street2:
                address.append(str(self.street2))
            if self.state_id and self.state_id.code == 'BKK':
                if self.sub_district_id:
                    address.append('แขวง' + str(self.sub_district_id.name))
                if self.district_id:
                    address.append('เขต' + str(self.district_id.name))
                elif self.city:
                    address.append('เขต' + str(self.city))
                address.append(str(self.state_id.name))
            elif self.state_id:
                if self.sub_district_id:
                    address.append('ตำบล' + str(self.sub_district_id.name))
                if self.district_id:
                    address.append('อำเภอ' + str(self.district_id.name))
                elif self.city:
                    address.append('อำเภอ' + str(self.city))
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
        if self.zip:
            address.append(str(self.zip))

        return address


