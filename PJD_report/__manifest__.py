# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]

{
    'name' : 'Print Accounting Monthly Report',
    'version' : '16.0.0.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Accounting Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base','account','account_accountant','thai_accounting'],
    'data' : [

        'report/report_reg.xml',
        'report/sale_tax_report.xml',
        'report/sale_tax_report2.xml',
        'report/purchase_tax_report.xml',
        'views/tax_report_view.xml',
        'security/ir.model.access.csv',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
