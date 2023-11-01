# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Itaas Orders Line Number',
    'description': 'Add Orders Line Number',
    'version': '16.0.0.1',
    'category': 'Purchase',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'purchase','sale','stock','mrp','account','purchase_request','product'
    ],
    'data': [
        # 'views/purchase_order_view.xml',
        'views/product_attribute_view.xml',
        # 'views/sale_order_view.xml',
        # 'views/stock_picking_view.xml',
        # 'views/manufacturing_orders_view.xml',
        # 'views/account_move_views.xml',
        # 'views/purchase_requests.xml',
        # # 'views/purchase_requests_line_orders_view.xml',
        # 'views/bills_of_materials_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
