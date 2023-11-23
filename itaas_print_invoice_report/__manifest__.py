# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Copyright (C) 2022 (www.itaas.co.th)

{
    'name': 'Print Accounting - Invoice Report',
    'version': '16.0.0.1',
    'price': 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary': 'Print Accounting Invoice Report',
    'description': """
                Accounting Report:
                    - ใบแจ้งหนี้/ใบส่งของ
                    - ใบกำกับภาษี
                    - ใบแจ้งหนี้/ใบกำกับภาษี
                    - ใบเสร็จรับเงิน
                    - ใบกำกับภาษี/ใบเสร็จรับเงิน
                    - ใบลดหนี้
                    - ใบเพิ่มหนี้
                    - บิลเงินสด
                    - ใบรับเงินมัดจำ
                    - ใบกำกับภาษี(แบบกระดาษต่อเนื่อง)
            """,
    'author': 'IT as a Service Co., Ltd.',
    'website': 'www.itaas.co.th',
    'depends': ['account', 'itaas_company_detail_address'],
    'data': [

        'views/res_config_settings_view.xml',

        'report/invoice_report.xml',
        'report/invoice_and_tax_invoice_report.xml',
        'report/tax_invoice_report.xml',
        'report/receipt_report.xml',
        # 'report/tax_invoice_and_receipt_report.xml',
        'report/creditnote_report.xml',
        'report/debitnote_report.xml',
        'report/down_payment_report.xml',
        'report/invoice_billing_report.xml',
        'report/tax_invoice_delivery_report.xml',
        'report/receipt_tax_invoice_report.xml',
        # This is example for DOT
        'report/invoice_report_dot.xml',
        'report/report_reg.xml',

    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
