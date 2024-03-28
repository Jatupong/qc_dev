# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name': 'Itaas Print Sales Report',
    'version': '16.0.1.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Sales',
    'summary': 'Sales Report',
    'description': """
                Quotations and Sales Order Report:
                - ใบเสนอราคา/Quotation
                - ใบส่งของชั่วคราว
                - ใบสั่งขาย/ใบเสนอราคา
Tags: 
Sales report
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['sale','itaas_image_signature'],
    'data': [

        
        'report/quotation_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
