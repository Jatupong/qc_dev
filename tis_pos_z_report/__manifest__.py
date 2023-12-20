# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.
{
    'name': 'POS SESSION SUMMARY / THERMAL SESSION SUMMARY REPORT / POS Z REPORT ',
    'version': '15.0.0.0.1',
    'summary': """ Pos session summary thermal report""",
    'description': """Pos session summary thermal report""",
    'category': 'Point of Sale',
    'price': 25,
    'currency': 'EUR',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': "http://www.technaureus.com/",
    'license': 'Other proprietary',
    'depends': ['point_of_sale'],
    
    'data': [
        'data/paper_format.xml',
        'report/invoice_external_layout.xml',
        'report/report_invoice.xml',
        'report/session_report.xml',
        'report/new_report_saledetails.xml',

    ],
    'qweb': [],
    'images': ['images/main_screenshot.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
