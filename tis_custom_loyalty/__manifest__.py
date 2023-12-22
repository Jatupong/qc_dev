# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

{
    'name': "Itaas Partner Domain",
    'version': '16.0.0.1',
    'sequence': 1,
    'author': "Technaureus Info Solutions Pvt. Ltd.",
    'website': "https://www.technaureus.com/",
    'category': 'Sales/Sales',
    'summary': "Partner Domain",
    'description': "Partner Domain",
    'depends': ['website_sale', 'point_of_sale', 'sale_management', 'loyalty'],
    'data': [
        'views/loyalty_rule_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'tis_custom_loyalty/static/src/js/loyalty.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,

}
