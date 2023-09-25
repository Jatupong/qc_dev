# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC Add Colum and Field',
    'version': '16.0.0.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'sale',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': [ 'base','product', 'sale', 'stock'],
    'data': [

        'security/ir.model.access.csv',
        'views/add_field_in_customers.xml',
        'views/customer_view.xml',
        'views/add_field_in_payment_term.xml',

    ],
    # 'demo': [
    #     'demo.xml'
    # ],

    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
