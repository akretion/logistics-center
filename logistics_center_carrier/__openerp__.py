# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   Copyright (C) 2012 Akretion David BEAL <david.beal@akretion.com>
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################


{
    'name': 'Logistics center carrier',
    'version': '0.2',
    'category': 'Warehouse',
    'summary': "Binding between OpenERP and logistics center carriers",
    'description': """
Binding between OpenERP and logistics center carriers""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'connector_logistics_center',
    ],
    'data': [
        'delivery_view.xml',
    ],
    'demo': [],
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
