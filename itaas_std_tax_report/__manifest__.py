# -*- coding: utf-8 -*-
# Part of ITAAS (www.itaas.co.th)

{
    'name': 'Itaas Std Tax Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Itaas Std Tax Report',
    'summary': 'Itaas Std Tax Report',
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base','account','itaas_partner_detail_address','itaas_company_detail_address','purchase','sale'],
    'data': [
        #wizard
        'wizard/tax_report_view.xml',
        # views
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/account_account_view.xml',
        'views/purchase_and_sale_tax_menu.xml',
        'views/account_journal_view.xml',
        # report
        'report/sale_tax_report.xml',
        'report/purchase_tax_report.xml',
        #security
        'security/ir.model.access.csv',
    ],

    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
