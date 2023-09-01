# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today ITAAS
{
    'name': 'Itaas Partner Detail Address',
    'version': '16.0.1.1',
    'sequence': 1,
    'category': 'base',
    'summary': 'Partner Detail Address',
    'author': 'ITAAS',
    'website': 'http://www.itaas.co.th/',
    'description': """
This module is for partner detail address
        """,
    'depends': ['base'],
    'data': [

        'security/ir.model.access.csv',
        'views/res_district_view.xml',
        'views/res_subdistrict_view.xml',
        'views/res_partner_view.xml',
        # Data
        # 'data/res_country_data.xml',
        'data/res_state_data.xml',
        'data/res_district_data.xml',
        'data/res_sub_district_data.xml',

    ],
    'images': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
