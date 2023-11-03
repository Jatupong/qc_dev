# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'Itaas Bank Detail',
    'version': '16.0.1.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'base',
    'summary': 'Bank More Detail',
    'description': """
                Bank Information
                for report
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base'],
    'data': [

        'views/res_bank_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
