# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            help="Upper quantity replied, by logistics center, "
                 "for the first line"
        ),
        'qty_lower': fields.boolean(
            'qty-1',
            help="Lower quantity replied, by logistics center, "
                 "for the second line"
        ),
    }

    def get_replied_qty(
            self, cr, uid, ids, count, move, picking, context=None):
        replied_qty = move.product_qty
        if count == 1 and picking.qty_upper:
            replied_qty += 1
        if count == 2 and picking.qty_lower:
            replied_qty -= 1
        return replied_qty


class StockPicking(orm.Model):
    _inherit = ['stock.picking', 'abstract.picking']
    _name = 'stock.picking'


class StockPickOut(orm.Model):
    _inherit = ['stock.picking.out', 'abstract.picking']
    _name = 'stock.picking.out'

    def button_simulate_logistic_response(self, cr, uid, ids, context=None):
        "Override this method in your module"
        parent = super(StockPickOut, self).button_simulate_logistic_response(
            cr, uid, ids, context=context)
        if not parent:
            picking = self.browse(cr, uid, ids[0], context=context)
            tpl = str(picking.id) + ','
            fbuffer = ''
            for move in picking.move_lines:
                fbuffer += tpl + str(move.product_id.id) + ','
                fbuffer += str(move.product_qty) + ',_,my_carrier,\n'
            name = 'my logistics center deliveries' + \
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
            name = 'my logistics center incoming' + \
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
