# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022 (www.itaas.co.th)

{
    'name': 'Print Accounting - Billing Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary': 'Print Accounting Billing Report',
    'description': """
                Billing Report:
                    - ใบวางบิล
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['thai_accounting', 'itaas_company_detail_address','base'],
    'data': [

        'views/res_config_settings_view.xml',

        'report/customer_billing_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
