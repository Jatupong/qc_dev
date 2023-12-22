# -*- coding: utf-8 -*-

{
    'name': 'OCT Pos Config',
    'version': '15.0.3.3',
    'category': 'POS',
    'summary': 'OCT Pos Config',
    'description': 'OCT Pos Config',
    'sequence': '1',
    'author': 'Odoo Developers',
    'depends': ['base','point_of_sale','operating_unit','hr',],
    'demo': [],
    
    'data': [
        'views/pos_view_form.xml',
        
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
