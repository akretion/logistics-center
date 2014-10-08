# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author David BEAL <david.beal@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Connector logistics center',
    'version': '0.8',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Common module for logistics center and external warehouse",
    'description': """
Connector logistics center
==========================

Description
-----------

Common module for logistics center and external warehouse management with csv file

Export :

- catalog
- products to receive
- products to deliver

Import :

- catalog inventory
- received products
- sent products


Implementation example
----------------------
see module Belspeed Logistic in the same branch


Branch dependencies
-------------------
* lp:file-exchange
* lp:~akretion-team/+junk/poc-import-data

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'sale_exceptions',
        'purchase',
        'connector_base_product',
        'connector_buffer',
        'file_repository',
    ],
    'external_dependencies': {
        'Python': ['unicodecsv'],
    },
    'data': [
        'backend_view.xml',
        'logistic_view.xml',
        'stock_view.xml',
        'sale_view.xml',
        'purchase_view.xml',
        'file_exchange_view.xml',
        'data/sale_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
    ],
    'css': [
    ],
    'js': [
    ],
    'qweb': [
    ],
}
