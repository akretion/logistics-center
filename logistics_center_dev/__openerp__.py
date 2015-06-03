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
    'name': 'Logistics center development tool',
    'version': '0.5',
    'category': 'stock',
    'sequence': 10,
    'summary': "Add features to help coding a new logistics center",
    'description': """
This module allows to :

  - **simulate logistic center reply** by adding a button on stock picking out
    and incoming views to trigger a file reception in file.document.
    You have to override defined methods to format this reply
    for your own logistics center.
  - **provide a debug mode** in backend.logistic : in this mode,
    file.document are created  with 'active' field to False
    (it'll not be sent by cron).
    You may implement a customized behavior, as define column names
    in data produced files and add 'required' field mark
    example: see 'set_header_file' method in Bleckmann class
    (module bleckmann_logistics/output.py).
  - **inactive some crons** (ie 'queue job') at the installation of this module
    and reactivate them (if they were active) at the module uninstall step.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'connector_logistics_center',
    ],
    'data': [
        'logistic_view.xml',
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
