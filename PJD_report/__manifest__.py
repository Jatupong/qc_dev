# -*- coding: utf-8 -*-


{
    'name' : 'Print Monthly report',
    'version' : '13.0.3.4',
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
