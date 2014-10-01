# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   Copyright (C) 2013 Akretion David BEAL <david.beal@akretion.com>
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

from openerp.osv import orm, fields

class res_country(orm.Model):

    _inherit = "res.country"

    _columns = {
        'alpha3': fields.char(
            'Alpha 3',
            size=3,
            help='code matching countries with ISO 3166-1 alpha3'),
        'numeric': fields.integer(
            'Numeric code',
            help='code matching countries with ISO 3166-1 numeric'),
    }

    _sql_constraints = [
        ('alpha3_uniq', 'unique (alpha3)',
            "The 'alpha3' field of the country must be unique !"),
        ('numeric_uniq', 'unique (numeric)',
            "The 'numeric' field of the country must be unique !"),
    ]
