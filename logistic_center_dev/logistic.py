# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author David BEAL <david.beal@akretion.com>
#     @author Sebastien BEAU <sebastien.beau@akretion.com>
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

from openerp.osv import orm, fields


class LogisticBackend(orm.Model):
    _inherit = 'logistic.backend'

    DEBUG_DISPLAY_COLUMN = False

    _columns = {
        'logistic_debug': fields.boolean(
            'Logistic Debug',
            help="Allow to generate 'File document' in debug mode"
            "(see module description for more help)"),
        'column_in_file': fields.boolean(
            'Column name ',
            help="Allow to display column names in csv files if implemented by "
            "your logistic module (file.document must be created "
            "with active filed to False)"),
    }

    _defaults = {
        'logistic_debug': True,
        'column_in_file': False,
    }

    def logistic_debug_mode(self, cr, uid, ids, context=None):
        for backend in self.browse(cr, uid, ids, context=context):
            if backend.logistic_debug:
                self.LOGISTIC_DEBUG = True
            else:
                self.LOGISTIC_DEBUG = False
            if backend.column_in_file:
                self.DEBUG_DISPLAY_COLUMN = True

