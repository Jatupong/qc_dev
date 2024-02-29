# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# 16.0.1.0
# 26/11/2022
#
#
#------------
{
    "name": "Thailand Accounting Enhancement for Odoo Enterprise",
    "category": 'Accounting',
    'summary': 'Thailand Accounting Enhancement.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '16.0.1.0',
    "depends": ['account', 'account_debit_note'],
    "external_dependencies" : {
        'python' : ['bahttext',
                    'num2words',
                    'xlrd'],
    },
    "data": [
        'data/sequence.xml',
        'views/res_partner_view.xml',
        #########################Next View###################
        'views/account_account_view.xml',
        'views/account_journal_view.xml',
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/account_move_reversal_view.xml',
        'views/account_cheque_statement_view.xml',
        'views/account_payment_register_view.xml',
        'views/account_payment_view.xml',
        'views/customer_billing_view.xml',
        #confirm multiple check
        'wizard/check_multiple_confirm_views.xml',

        # data fro preload ###
        'data/account_wht_data.xml',
        # security access and rule
        'security/ir.model.access.csv',
        'security/security_group.xml',


    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}