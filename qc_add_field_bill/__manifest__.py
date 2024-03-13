# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:12|M:03|Y:2024]
{
    "name": "Add Field Product",
    "version": "16.0.0.0.0",
    "summary": "Add Field in model [Product] and [Sale Order Line]",
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    "category": 'itaas',
    "license": "AGPL-3",
    'depends': ['product', 'base','sale','product_volume'],
    "data": [
        'views/account_add_field_view.xml',
        'views/edit_view_purchase_tax_report.xml',
    ],
    "installable": True,
    "auto_install": False,
}