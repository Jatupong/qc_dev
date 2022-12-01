# -*- coding: utf-8 -*-

{
    'name' : 'BOM Capacity Planing',
    'version' : '16.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'BOM Capacity Planing',
    'summary' : 'BOM Capacity Planing',
    'description': """
                BOM Capacity Planing:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['mrp'],
    'data' : [
        # 'views/res_company_view.xml',
        'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
        'views/product_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
