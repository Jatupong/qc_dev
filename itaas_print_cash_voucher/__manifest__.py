# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
#13.0.2.1 edit By Jeng 16-06-2021 รายงานเงินสดย่อย
#13.0.2.2 edit By Jeng 22-06-2021 รายงานเงินสดย่อย แก้เพิ่ม
{
    "name": "Itaas Print Cash Voucher",
    "author": "Itaas Print Bank",
    'version' : '15.0.0.1',
    "category": "mrp",
    "website": "www.itaas.co.th",
    "depends": ['account','hr'],
    "data": [
        'report/debitcredit_report06.xml',
        'report/cash_register_report.xml',
        'report/report_reg.xml',
        'views/sequence.xml',
        # 'views/cash_register.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
