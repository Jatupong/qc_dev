# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
#13.0.2.1 - 19/06/2021 - remove tax_inv_generated_1,sequence_receipt no need
#13.0.2.2 - 23/08/2021 - add fucntion to auto reverse tax on payment screen
#16.0.1.1 - 29/04/2023 - add is_debit_note to correct sequence
{
    "name": "Itaas Gen Tax Invoice Date",
    'version': '16.0.1.1',
    "category": 'itaas',
    'summary': 'Itaas Gen Tax Invoice Date.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base','account','thai_accounting','itaas_generate_tax'],
    "data": [
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
