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

from openerp.osv import orm
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def distinct_logistic_backend_version(self, cr, uid, ids, context=None):
        """ Check if sale order 'logistic center' version match with
            the product logistic backend version
        """
        line = self.browse(cr, uid, ids, context=context)[0]
        backend = line.order_id.get_logistic_backend()
        if backend:
            if not line.product_id.logistic_bind_ids:
                return True
            if backend and backend.version:
                for bind in line.product_id.logistic_bind_ids:
                    if bind.backend_id and bind.backend_id.version \
                            and bind.backend_id.version != backend.version:
                        return True
        return False

    def logistic_center_catalog_outofdate(self, cr, uid, ids, line,
                                          task_method, context=None):
        """Check if product write_date is > last task execution date"""
        backend = line.order_id.get_logistic_backend()
        if backend:
            catalog_task_ids = self.pool['repository.task'].search(cr, uid, [
                ('repository_id', '=', backend.file_repository_id.id),
                ('method', '=', task_method),
            ], context=context)
            assert len(catalog_task_ids) == 1, "Will only take one task id"
            task = self.pool['repository.task'].browse(cr, uid, catalog_task_ids[0],
                                                       context=context)
            if task.last_exe_date:
                #TODO : evaluate if this query must be applied
                #on the whole products of the sale order (-> sale.order)
                query = """
SELECT GREATEST (pt.write_date, pp.write_date) AS update_date
FROM product_template pt LEFT JOIN product_product pp
    ON pp.product_tmpl_id = pt.id
WHERE pp.id = %s """ % line.product_id.id
                cr.execute(query)
                product_date = cr.fetchall()[0][0]
                if product_date > task.last_exe_date:
                    return True
            else:
                return True
            return False
        return False


class SaleOrder(orm.Model):
    _inherit = ['sale.order', 'abstract.logistic.flow']
    _name = 'sale.order'

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,
                                 date_planned, context=None):
        vals = super(SaleOrder, self)._prepare_order_line_move(
            cr, uid, order, line, picking_id, date_planned, context=context)
        backend = self.get_logistic_backend(cr, uid, [order.id], context=context)
        if backend:
            location_id = backend.warehouse_id.lot_stock_id.id
            location_dest_id = backend.warehouse_id.lot_output_id.id
            if location_id and location_dest_id:
                vals['location_id'] = location_id
                vals['location_dest_id'] = location_dest_id
            else:
                raise orm.except_orm(_("Warehouse settings error: "),
                                     _(self.WAREHOUSE_EXCEPTION
                                     % (backend.warehouse_id.name)))
            vals['logistic_center'] = order.logistic_center
        return vals

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(SaleOrder, self)._prepare_order_picking(
            cr, uid, order, context=context)
        vals['logistic_center'] = order.logistic_center
        return vals

    def onchange_shop_id(self, cr, uid, ids, shop_id, context, partner_id,
                         partner_invoice_id, partner_shhipping_id):
        res = super(SaleOrder, self).onchange_shop_id(
            cr, uid, ids, shop_id, context, partner_invoice_id, partner_shhipping_id)
        if shop_id:
            values = res['value']
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
            values.update({'logistic_center': 'internal'})
            if shop.warehouse_id:
                logistic_center = self.get_logistic_backend(
                    cr, uid, [shop.warehouse_id.id], origin='warehouse',
                    context=context)
                res['value'].update({'logistic_center': logistic_center})
        return res

