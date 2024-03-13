# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022-today www.itaas.co.th (Dev K.Book)

{
    'name': 'Print Accounting Cheque Report',
    'version': '16.0.1.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'description': """
                Accounting Report:
                    - Cheque Report
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['account', 'account_accountant', 'thai_accounting'],
    'data': [

        'views/view_res_bank_form.xml',
        'report/cheque_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
