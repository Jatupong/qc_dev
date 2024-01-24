# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022 (www.itaas.co.th)

{
    'name': 'Print Stock Picking Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Stock',
    'summary': 'Print Stock Picking Report',
    'description': """
                Stock Report:
                    - Internal Transfer Report
                    - Delivery Note Report
                    - Receipt Note Report
                    - ใบส่งคืนสินค้า
                    - ใบรับคืนสินค้า
                    - ใบเบิกพัสดุ
                    """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['stock', 'itaas_company_detail_address', 'itaas_image_signature'],
    'data': [

        'views/res_config_settings_view.xml',
        # 'report/internal_transfer_report.xml',
        'report/delivery_report.xml',
        # 'report/receipt_report.xml',
        'report/return_in_report.xml',
        'report/return_out_report.xml',
        'report/product_bill_report.xml',
        'report/product_bill_report02.xml',
        'report/product_bill_report06.xml',
        'report/product_bill_report07.xml',
        'report/product_bill_report03.xml',
        'report/bill_of_lading.xml',
        'report/packing_list.xml',

        'wizard/stock_count_wizard_view.xml',
        'report/stock_count_report.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
