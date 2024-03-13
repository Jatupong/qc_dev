# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:02|Y:2024]

{
    'name': 'QC. Add Tree From At Pricelist',
    'version': '16.0.0.0',
    'category': 'base',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base','sale','product','qc_sale_order','qc_sale_order_state'],
    'data': [
        'views/product_pricelist_item_view.xml',
        'views/product_pricelist_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
