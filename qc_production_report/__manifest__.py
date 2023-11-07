# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2023-today www.itaas.co.th (Dev K.Book)

{
    'name': 'QC. production report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Stock',
    'summary': '',
    'description': """
                """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['mrp', 'itaas_company_detail_address', 'itaas_company_setting', 'qc_sale_order'],
    'data': [

        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
        'report/qc_production_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
