# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# 13.0.1.0 - first asset for v13
# 13.0.2.0 - update version
# 13.0.2.1 - 20/06/2021
# correct disposal process with last 2 line
# correct sell process and amount on asset
# complete asset movement record
# asset multi confirm
# Add disposal type update on the asset (sell or dispose (write off)
#-------------------------------------------------------------------
# 15.0.1.0 - 2/08/2022
{
    "name": "Thailand Asset Management by ITAAS",
    'version': '16.0.1.0',
    "category": 'itaas',
    'summary': 'Asset Management',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base','account','account_asset','hr'],
    "data": [
        'views/view_account_asset_form.xml',
        'wizard/asset_move_wizard_view.xml',
        'wizard/asset_multi_confirm_view.xml',
        'views/view_account_move_form.xml',
        'views/sequence.xml',
        'security/ir.model.access.csv',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
