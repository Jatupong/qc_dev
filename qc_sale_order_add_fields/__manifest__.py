# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. Sale Order Add Fields',
    'version': '16.0.0.1',
    'category': 'base',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base','sale','product','qc_sale_quotations_edit_name'],
    'data': [

        'views/sale_order_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
