# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'Stron Create Maintenance Equipment',
    'version': '16.0.0.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'maintenance',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['product', 'sale', 'stock', 'maintenance'],
    'data': [

        'views/maintenance_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
