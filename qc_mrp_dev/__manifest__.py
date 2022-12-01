# -*- coding: utf-8 -*-
# Part of ITAAS (www.itaas.co.th)
#13.0.1.1 add field for report Invoice
#13.0.2.0 - intial new version
#13.0.2.1 - add check customer tax id state
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
