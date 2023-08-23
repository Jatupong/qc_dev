# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Itaas Generate Sequence",
    'version': '16.0.1.0',
    "category": 'itaas',
    'summary': 'Generate Sequence.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base'],
    "data": [
        'security/ir.model.access.csv',
        'views/sequence_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
