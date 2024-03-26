# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. Sale Quotations',
    'version': '16.0.0.1',
    'category': 'base',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base','sale'],
    'data': [


        'security/ir.model.access.csv',
        'views/sale_quotatios_view.xml',
        'views/department_view.xml',
        'views/box_type_view.xml',
        'views/loading_type_view.xml',
        'views/urgent_need_view.xml',
        'views/want_to_deliver_view.xml',
        'views/Importance_view.xml',
        'views/container_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
