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

import base64
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def button_simulate_logistic_response(
            self, cr, uid, ids, context=None):
        picking = self.browse(cr, uid, ids[0], context=context)
        tpl = 'ODC;' + str(picking.id) + ';_;'
        fbuffer = ''
        count = 0
        for move in picking.move_lines:
            count += 1
            replied_qty = self.get_replied_qty(
                cr, uid, ids, count, move, picking, context=context)
            fbuffer += tpl + str(move.product_id.id) + '.ZZ;990099;'
            fbuffer += str(replied_qty) + ';_;DHL;_;;Complete\n'
        name = 'BELSPEED-CONTAINER-' + \
            datetime.now().strftime('%Y%m%d%H%M%S')
        model, res_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'bleckmann_logistics', 'bleckmann_ftp')
        vals = {
            'name': name,
            'sequence': '200',
            'datas': base64.encodestring(fbuffer),
            'active': True,
            'state': 'waiting',
            'direction': 'input',
            'repository_id': res_id,
            'file_type': 'logistic_delivery',
            'type': 'binary',
            'datas_fname': name + '.txt',
            'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        }
        return self.pool['file.document'].create(cr, uid, vals, context=context)


class StockPickingIn(orm.Model):
    _inherit = 'stock.picking.in'

    def button_simulate_logistic_response(
            self, cr, uid, ids, context=None):
        picking = self.browse(cr, uid, ids[0], context=context)
        tpl = 'PAL;' + str(picking.id) + ';'
        fbuffer = ''
        count = 0
        for move in picking.move_lines:
            count += 1
            replied_qty = self.get_replied_qty(
                cr, uid, ids, count, move, picking, context=context)
            fbuffer += tpl + str(move.id) + ';'
            fbuffer += str(move.product_id.id) + '.ZZ;990099;'
            fbuffer += str(move.product_qty) + ';' + str(replied_qty)
            fbuffer += ';_\n'
        name = 'BELSPEED-EXTRACT-' + \
            datetime.now().strftime('%Y%m%d%H%M%S')
        model, res_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'bleckmann_logistics', 'bleckmann_ftp')
        vals = {
            'name': name,
            'sequence': '200',
            'datas': base64.encodestring(fbuffer),
            'active': True,
            'state': 'waiting',
            'direction': 'input',
            'repository_id': res_id,
            'file_type': 'logistic_incoming',
            'type': 'binary',
            'datas_fname': name + '.txt',
            'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        }
        return self.pool['file.document'].create(cr, uid, vals, context=context)

