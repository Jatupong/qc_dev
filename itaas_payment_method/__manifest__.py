# -*- coding: utf-8 -*-
# Part of ITAAS (www.itaas.co.th)
# ยังไม่ชัดเจนเรื่องการนำไปใช้
# สร้างไว้กับ partner แล้วเอาใช้ยังไงต่อ
{
    'name' : 'Itaas Payment Method',
    'version' : '16.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : '',
    'description': """
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','purchase','base','account',],
    'data' : [
        'views/payment_method_type_view.xml',
        'views/account_move.xml',
        'views/res_partner.xml',
        'security/ir.model.access.csv',

    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
