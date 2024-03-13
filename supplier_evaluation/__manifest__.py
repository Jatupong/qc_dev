# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
# Moved from [smeone_dev] on [D:13|M:03|Y:2024] By Sarawut Ph.

{
    'name' : 'Supplier Evaluation',
    'version': '11.0.1.2.0',
    "category": "purchase",
    'author': 'IT as a Service Co., Ltd.',
    'website': 'http://www.itaas.co.th/',
    'license': 'AGPL-3',
    "depends": ['purchase'],
    "data": [
        'security/ir.model.access.csv',
        # supplier_evaluation
        'views/view_supplier_evaluation.xml',
        'views/res_partner_view.xml',
        # Report
        'report/report_reg.xml',
        'report/assessment_form_report.xml',
        # wizard
        # 'wizard/supplier_evaluation_report_view.xml',
        'report/summary_supplier_evaluation_report.xml'


    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
