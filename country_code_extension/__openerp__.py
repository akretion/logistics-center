# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   Copyright (C) 2014 Akretion David BEAL <david.beal@akretion.com>
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
    'name': 'Country code extension',
    'version': '0.1',
    'category': 'Warehouse',
    'summary': "Country codes extension from ISO 3166-1",
    'description': """
Add alternative codes to base country codes :

- numeric code : ISO 3166-1 numeric
- three letter code : ISO 3166-1 alpha-3

These alternatives maybe used by logistic partners

The datas comes from http://opengeocode.org/download.php
try this : http://download.geonames.org/export/dump/countryInfo.txt
""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'base',
    ],
    'data': [
        'res.country.csv',
        'country_view.xml',
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
