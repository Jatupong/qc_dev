# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Jirat.Ph [D:25|M:03|Y:2024]
{
    "name": "Add Field Setting",
    "version": "16.0.0.0.0",
    "summary": "Add Field Setting in model [res.company] ",
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    "category": 'itaas',
    "license": "AGPL-3",
    'depends': ['base','itaas_company_detail_address', 'itaas_partner_detail_address','itaas_contact_person',],
    "data": [
        
        # 'views/res_company.xml',
        'views/res_config_settings_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
