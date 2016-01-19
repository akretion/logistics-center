# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(orm.Model):
    _inherit = ['purchase.order', 'abstract.logistic.flow']
    _name = 'purchase.order'

    def __init__(self, pool, cr):
        super(PurchaseOrder, self).__init__(pool, cr)
        self._columns['warehouse_id'].required = True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(PurchaseOrder, self)._prepare_order_picking(
            cr, uid, order, context=context)
        vals['logistic_center'] = order.logistic_center
        return vals

    def onchange_logistic_center(self, cr, uid, ids, logistic_center, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if logistic_center and logistic_center != 'internal':
                logistic_id = int(logistic_center)
                backend = self.pool['logistic.backend'].browse(
                    cr, uid, logistic_id, context=None)
                location_id = backend.warehouse_id.lot_stock_id.id
            else:
                if order.warehouse_id:
                    location_id = order.warehouse_id.lot_stock_id.id
            if location_id:
                return {'value': {'location_id': location_id}}
        return True

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id):
        "Set logistic_center according warehouse_id"
        res = super(PurchaseOrder, self).onchange_warehouse_id(
            cr, uid, ids, warehouse_id)
        if warehouse_id:
            logistic_center = self.get_logistic_backend(
                cr, uid, [warehouse_id], origin='warehouse')
            if logistic_center:
                logistic_center = str(logistic_center)
            res['value'].update({'logistic_center': logistic_center})
        return res
