# -*- coding: utf-8 -*-
#############################################################################

{
    'name': "Wizard Stock Custom Report",
    'version': '16.0.1.1',
    'description': """""",
    'author': "ITAAS",
    'company': 'ITAAS',
    'website': "https://www.itaas.co.th",
    'category': 'Accounting',
    'depends': ['base','account','stock','purchase_stock',],
    'data':
        [
            #security
            'security/ir.model.access.csv',

            #views
            'views/return_card_report_view.xml',
            # 'views/stock_picking_view.xml',
            'views/product_purchase_report_view.xml'
        ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
