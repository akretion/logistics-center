# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from .common import SKU_SUFFIX
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
            fbuffer += '%s%s%s%s' % (
                tpl, str(move.product_id.default_code), SKU_SUFFIX, ';990099;')
            fbuffer += str(replied_qty) + ';_;DHL;_;;Complete\n'
        name = 'BLECKMANN-CONTAINER-' + \
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
        return self.pool['file.document'].create(
            cr, uid, vals, context=context)


class StockPickingIn(orm.Model):
    _inherit = 'stock.picking.in'

    def button_simulate_logistic_response(
            self, cr, uid, ids, context=None):
        picking = self.browse(cr, uid, ids[0], context=context)
        tpl = 'PAL;%s;' % str(picking.id)
        fbuffer = ''
        count = 0
        for move in picking.move_lines:
            count += 1
            replied_qty = self.get_replied_qty(
                cr, uid, ids, count, move, picking, context=context)
            fbuffer += tpl + str(move.id) + ';'
            fbuffer += '%s%s;990099;' % (
                str(move.product_id.default_code), SKU_SUFFIX)
            fbuffer += str(move.product_qty) + ';' + str(replied_qty)
            fbuffer += ';_\n'
        name = 'BLECKMANN-EXTRACT-' + \
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
        return self.pool['file.document'].create(
            cr, uid, vals, context=context)
