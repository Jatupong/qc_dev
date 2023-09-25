# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name': 'Itaas Print Purcase Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Purchase',
    'summary': 'Purchase Report',
    'description': """
                Purchase Order Report:
                - ใบสั่งซื้อในประเทศ
                - ใบสั่งซื้อต่างประเทศ
Tags: 
Purchase report
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['purchase', 'itaas_company_detail_address', 'itaas_partner_detail_address',
                'itaas_contact_person', 'itaas_image_signature','base'],
    'data': [

        'views/res_config_settings_view.xml',
        'views/res_company.xml',
        'views/purchase_order_view.xml',
        'report/purchase_order_report.xml',
        'report/purchase_order_inter_report.xml',
        'report/purchase_request_report.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
