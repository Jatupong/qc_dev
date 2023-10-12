# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. Quality Control',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Quality',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['quality_control', 'hr', 'mrp'],
    'data': [

        'security/ir.model.access.csv',
        'views/quality_alert_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
