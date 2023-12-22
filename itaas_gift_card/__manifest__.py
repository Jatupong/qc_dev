# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Itaas Gift Card",
    'version': '16.0.0.0',
    "category": 'itaas',
    'summary': 'Itaas Gift Card.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base','loyalty','pos_loyalty','sale_loyalty','sale','point_of_sale'],
    "data": [
        #security
        'security/ir.model.access.csv',
        #views
        'views/loyalty_card_form.xml',
        'views/loyalty_program_form.xml',
        #wizard
        'wizard/loyalty_program_form.xml',
        'wizard/loyalty_program_menu.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
