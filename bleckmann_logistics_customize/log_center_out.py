# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
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

from openerp.osv import orm
from openerp.addons.bleckmann_logistics.output import Bleckmann, sanitize
from .log_center import BACKEND_VERSION


class LogisticBackendMine(orm.Model):
    _inherit = 'logistic.backend'

    def select_versions(self, cr, uid, context=None):
        """ Available versions
        """
        selected = super(LogisticBackendMine, self).select_versions(
            cr, uid, context=context)
        selected.append((BACKEND_VERSION, BACKEND_VERSION.capitalize()))
        return selected

    def _prepare_doc_vals(self, cr, uid, backend_version, file_datas, model_ids,
                          flow, context=None):
        vals = super(LogisticBackendMine, self)._prepare_doc_vals(
            cr, uid, backend_version, file_datas, model_ids, flow, context=context)
        vals.update(
            {'datas_fname': BACKEND_VERSION + '_' + vals['datas_fname']})
        return vals


class BleckmannMine(Bleckmann):
    FROM_SITE_ID = 'XX'          # Bleckmann info
    CLIENT_ID = 'YYYYYYY'        # Bleckmann info

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == BACKEND_VERSION

    def __init__(self, *args, **kwargs):
        return super(BleckmannMine, self).__init__(self, *args, **kwargs)

    def prepare_picking(self, picking, fields_dict):
        vals = super(BleckmannMine, self).prepare_picking(picking, fields_dict)
        vals.update({
            'From Site Id': self.FROM_SITE_ID,
            'Client Id': self.CLIENT_ID,
            'Move Task Status': 'Released',
            'Product Price': '0',
        })
        return vals

    def prepare_move(self, move, fields_dict):
        vals = super(BleckmannMine, self).prepare_move(move, fields_dict)
        vals.update({
            'User Def Type 5': 'My brand',  # brand
            'Client Id': self.CLIENT_ID,
        })
        return vals

    def prepare_catalog(self, product, fields_dict):
        vals = super(BleckmannMine, self).prepare_catalog(product, fields_dict)
        vals.update({
            # you may inherit this method
            # in your own module to change these value
            'Product Group': self.CLIENT_ID,
            'Putaway Group': self.CLIENT_ID,
            'Client Id': self.CLIENT_ID,
            'User Def Type 1': 'FRA',
            'User Def Type 7': sanitize('ZZZZZ'),   # example
            'Family Group': 'ZZZZZ',
        })
        return vals
