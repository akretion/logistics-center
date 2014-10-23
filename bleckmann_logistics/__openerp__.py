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
    'name': 'Bleckmann logistics center',
    'version': '0.7',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Bleckmann logistics center",
    'description': """
Bleckmann logistics center
===========================

Description
-----------

Logistic Bleckmann exchange management :

Export :

- catalog
- products to receive
- products to deliver

Import :

- catalog inventory
- received products
- sent products

Settings
--------

    * Define an new warehouse for your logistics center
    * Create a new Logistic backend (menu connector/logistic/backend)
      by selecting the existing 'file repository' ('Bleckmann')
    * Select the created warehouse in this logistics center and
      set a version or create a new one (see module bleckmann_logistic_customize)
    * Add one cron for each input task in the backend
    * You may add several crons in one click to have multiple executions
      per input task.

How to use
----------

    * 

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'connector_logistic_center',
    ],
    'external_dependencies': {
        'Python': [
            'unicodecsv',
            'pycountry',
        ],
    },
    'data': [
        'data/sale_data.xml',
        'data/repository_data.xml',
        'data/repository.task.csv',
        'data/backend_data.xml',
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
