# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022 (www.itaas.co.th)

{
    'name': 'Print Accounting - Payment Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary': 'Print Accounting Payment Report',
    'description': """
                Payment Report:
                    - ใบกำกับภาษี/ใบเสร็จรับเงิน
                    - ใบเสร็จรับเงิน
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['account', 'itaas_company_detail_address'],
    'data': [

        'report/tax_invoice_receipt_report.xml',
        'report/receipt_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}