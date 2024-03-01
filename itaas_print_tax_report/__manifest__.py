# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)
# '13.0.1', Open field wht_reference
# '13.0.2', edit sale_tax and purchase_tax
# '13.1.0', purchase and sale vat
# '13.0.2.0' update with warning for missing date and ref for sale and purchase tax report
# '13.0.2.1' add previous balance to include in pnd 30 and fix purchase report in excel to correct same with pdf
# '13.0.2.2' add wht text upload from complete one to this module
# '13.0.2.3' add pnd 3 53
# '13.0.2.4" 20/05/2020 - fix order of xml file
#  13.0.3.1 22/07/2021 - แก้ภาษีขายการดึง ฟิว untaxed เพราะเคส ท้ายบิลทำให้ดึงฟิวผิด
#  13.0.3.2 05/08/2021 - แก้ภาษีขาย เคส Journal Entry คีย์ตรง สามารถออกรายงานภาษีขายได้
#  13.0.3.2 แก้ Domain ภาษีขายให่ไมเจอรายการของ POS ที่มา INV

{
    'name' : 'Print Accounting Tax and WHT Report',
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
        'views/account_account.xml',
        # 'views/journal_form.xml',
        'views/purchase_form_inherit.xml',
        'views/account_move_view.xml',
        'report/teejai_report_journal_journal.xml',
        'report/teejai_report02_journal_1.xml',

        'report/report_reg.xml',
        'report/sale_tax_report.xml',
        # 'report/purchase_tax_report.xml',
        'report/report_taxsummary.xml',
        'report/report_pnd3.xml',
        'report/report_pnd53.xml',
        'report/holdingtax3_report.xml',
        'report/holdingtax53_report.xml',
        # 'report/teejai_report.xml',
        # 'report/teejai_report02.xml',
        'report/teejai_report02_journal.xml',
        'report/teejai_report_journal.xml',
        'report/teejai_report03_journal.xml',
        # 'views/tax_report_view.xml',
        'views/pnd_30_views_report.xml',
        'report/report_pnd30.xml',
        'views/res_company.xml',
        'security/ir.model.access.csv',

        'views/undue_purchase_tax_views.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
