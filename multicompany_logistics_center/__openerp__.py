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
    'name': 'Multicompany logistics center',
    'version': '0.8',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Multicompany backend logistics center ",
    'description': """
Multicompany logistics center
==============================

Description
-----------

Allow to use the same logistics backend for several companies.
Backend warehouse field becomes a property field.

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'connector_logistics_center',
    ],
    'external_dependencies': {
        'Python': [],
    },
    'data': [
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
