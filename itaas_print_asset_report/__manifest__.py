# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
# 13.0.1.0 - first asset for v13
# 13.0.2.0 - update version
# create asset report, depreciation board and asset movement
# change from old formt to new format
{
    "name": "ITAAS Print Asset Report",
    'version': '13.0.2.2',
    "category": 'itaas',
    'summary': 'Asset Management',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "depends": ['base','account','account_asset','hr','itaas_account_asset_management','account_asset'],
    "data": [
        'report/asset_report.xml',
        'report/asset_labels_report.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
