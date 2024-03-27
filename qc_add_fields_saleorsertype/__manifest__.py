# -*- coding: utf-8 -*-
# Part of IT as a Service Co., Ltd.
# Create By Sarawut.Ph [D:27|M:03|Y:2024]
{
    'name' : 'QC. Add Fields Sale Order Type',
    'version' : '16.0.0.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'System',
    'summary' : 'Edit Button And Add Fields',
    'description': """
                Add Fields:
                    - Sale Material [sale_material_bool]
                    - Sale Production [sale_production_bool]
                Edit Button:
                    - Send by Email
                    - Confirm Order
                    - Apply Set
                    - Create Invoice
                    - Done
                    - Pre-Production Order
                    - Set-Draft Order
                    - Set-Check Delivery 
                    - Production Order
                Create By Sarawut.Ph [D:27|M:03|Y:2024]
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends': ['base','sale','qc_sale_order_state'],
    'data' : [
        'views/sale_order_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "auto_install": False,
}