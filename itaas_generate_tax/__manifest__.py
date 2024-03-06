# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)
# 12.0.1.1 9/08/2021 แก้หน้า wizard ให้มี เดือน และ ปี  ส่วนที่จะส่งวันที่ 1 เสมอ
{
    'name' : 'ITAAS Generate Tax ',
    'version' : '13.0.1.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Generate Tax/Reverse Tax',
    'summary' : 'Generate Tax/Reverse Tax',
    'description': """
                Generate Tax/Reverse Tax
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['account','base','thai_accounting'],
    'data' : [
        'views/account_invoice.xml',
        'security/ir.model.access.csv',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
