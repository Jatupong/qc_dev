# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. Deposit Report',
    'version': '16.0.0.8',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Account',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['account', 'report_xlsx'],
    'data': [

        'security/ir.model.access.csv',
        'wizard/wizard_deposit_report_view.xml',
        'report/deposit_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
