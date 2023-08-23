# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd. (www.itaas.co.th)
{
    'name': 'Itaas Company Detail Address',
    'version': '16.0.1.0',
    'price': 'Free',
    'currency': 'THB',
    'category': 'base',
    'summary': 'Company Detail Address',
    'description': """
                Company Information
                for report
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['base'],
    'data': [

        'views/res_company_view.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
