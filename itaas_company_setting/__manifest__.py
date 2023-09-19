# -*- coding: utf-8 -*-
# Part of ITAAS (www.itaas.co.th)
#13.0.1.1 add field for report Invoice
#13.0.2.0 - intial new version
#13.0.2.1 - add check customer tax id state
{
    'name' : 'General Company Setting',
    'version' : '16.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'General Company Setting',
    'summary' : 'General Company Setting',
    'description': """
                General Company Setting:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base'],
    'data' : [
        'views/res_company_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
