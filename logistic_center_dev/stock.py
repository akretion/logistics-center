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
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AbstractStockPicking(orm.AbstractModel):
    _name = 'abstract.picking'

    _columns = {
        'qty_upper': fields.boolean(
            'qty+1',
            help="Upper quantity replied, by logistic center, for the first line"
        ),
        'qty_lower': fields.boolean(
            'qty-1',
            help="Lower quantity replied, by logistic center, for the second line"
        ),
    }

    def get_replied_qty(self, cr, uid, ids, count, move, picking, context=None):
        replied_qty = move.product_qty
        if count == 1 and picking.qty_upper:
            replied_qty += 1
        if count == 2 and picking.qty_lower:
            replied_qty -= 1
        return replied_qty


class StockPicking(orm.Model):
    _inherit = ['stock.picking', 'abstract.picking']
    _name = 'stock.picking'


class StockPickingOut(orm.Model):
    _inherit = ['stock.picking.out', 'abstract.picking']
    _name = 'stock.picking.out'

    def button_simulate_logistic_response(self, cr, uid, ids, context=None):
        "Override this method in your module"
        parent = super(StockPickingOut, self).button_simulate_logistic_response(
            cr, uid, ids, context=context)
        if not parent:
            picking = self.browse(cr, uid, ids[0], context=context)
            tpl = str(picking.id) + ','
            fbuffer = ''
            for move in picking.move_lines:
                fbuffer += tpl + str(move.product_id.id) + ','
                fbuffer += str(move.product_qty) + ',_,my_carrier,\n'
            name = 'my logistic center deliveries' + \
                datetime.now().strftime('%Y%m%d%H%M%S')
            vals = {
                'name': name,
                'sequence': '200',
                'datas': base64.encodestring(fbuffer),
                'active': True,
                'state': 'waiting',
                'direction': 'input',
                'file_type': 'logistic_delivery',
                'type': 'binary',
                'datas_fname': name + '.csv',
                'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
            parent = self.pool['file.document'].create(
                cr, uid, vals, context=context)
        vals = {'log_in_file_doc_id': parent}
        return self.write(cr, uid, ids, vals, context=context)


class StockPickingIn(orm.Model):
    _inherit = ['stock.picking.in', 'abstract.picking']
    _name = 'stock.picking.in'

    def button_simulate_logistic_response(self, cr, uid, ids, context=None):
        "Override this method in your module"
        parent = super(StockPickingIn, self).button_simulate_logistic_response(
            cr, uid, ids, context=context)
        if not parent:
            picking = self.browse(cr, uid, ids[0], context=context)
            tpl = str(picking.id) + ','
            fbuffer = ''
            for move in picking.move_lines:
                fbuffer += tpl + str(move.product_id.id) + ','
                fbuffer += str(move.product_qty) + ',_,\n'
            name = 'my logistic center incoming' + \
                datetime.now().strftime('%Y%m%d%H%M%S')
            vals = {
                'name': name,
                'sequence': '250',
                'datas': base64.encodestring(fbuffer),
                'active': True,
                'state': 'waiting',
                'direction': 'input',
                'file_type': 'logistic_incoming',
                'type': 'binary',
                'datas_fname': name + '.csv',
                'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
            parent = self.pool['file.document'].create(
                cr, uid, vals, context=context)
        vals = {'log_in_file_doc_id': parent}
        return self.write(cr, uid, ids, vals, context=context)

