# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. Sale Order Input',
    'version': '16.0.0.1',
    'category': 'base',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base','sale','product'],
    'data': [

        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/sale_order_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
