# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC Purchase Request Equipment',
    'version': '16.0.0.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'purchase',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['purchase','purchase_request'],
    'data': [

        'views/purchase_request.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
