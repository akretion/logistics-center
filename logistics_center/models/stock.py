# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
import logging

from odoo import api, models, fields, _


_logger = logging.getLogger(__name__)


LOGISTIC_FIELDS = [
    'log_out_file_doc_id',
    'log_in_file_doc_id',
    'logistics_center',
]


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _select_location_dest_id(self):
        location_dest_id = False
        logistics_center = context.get('logistics_center', False)
        if context['picking_type'] == 'in' \
                and logistics_center and logistics_center != 'internal':
            backend = self.pool['logistics.backend'].browse(int(logistics_center))
            location_dest_id = backend.warehouse_id.lot_stock_id.id
        return location_dest_id

    _defaults = {
        'location_dest_id': _select_location_dest_id
    }


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Implement your method in your module to check if required
    logistics_exception = fields.Boolean(
        string='Logistics Exception', copy=False,
        help="Checked if a wrong data prevent you to send "
             "the order to your logistics center")
    logistics_blocked = fields.Boolean(
        string='Logistics Blocked', copy=False,
        help="Logistics Delivery Orders can be blocked manually")
    log_out_file_doc_id = fields.Many2one(
        'ir.attachment',
        'Logistics Doc. Out',
        copy=False,
        help="Refers the 'File document' object which "
             "contains infmodelsations to send to "
             "Logistics center for synchronisation purpose.")
    log_in_file_doc_id = fields.Many2one(
        'ir.attachment',
        'Logistics Doc. In',
        readonly=True, copy=False,
        help="Refers the 'File document' object which "
             "contains infmodelsations sent by "
             "Logistics center in response from original message.")
    drop_date = fields.Date(
        string='Dépose marchandise',
        help="Date à laquelle le destinataire prendra "
             "possession des marchandises")

    def run_job(self, picking_id, file_doc_id, moves, picking_vals=None):
        # picking_id is extracted
        picking_id = int(picking_id)
        qty_by_prod = {}
        for move in moves:
            product_id = move["product_id"]
            qty = abs(float(move["product_qty"]))
            if qty_by_prod.get(product_id):
                qty_by_prod[product_id] += qty
            else:
                qty_by_prod[product_id] = qty
        self._validate_from_data(picking_id, qty_by_prod)
        if not picking_vals:
            picking_vals = {}
        picking_vals['log_in_file_doc_id'] = file_doc_id
        picking = self.browse(picking_id)
        linked_picking = picking
        if picking.log_out_file_doc_id:
            picking_vals['log_out_file_doc_id'] = (
                picking.log_out_file_doc_id.id)
        if picking.state != 'done' and picking.backorder_id:
            # we put file doc in backorder if picking validation is partial
            linked_picking = picking.backorder_id
        linked_picking.write(picking_vals)
        return True

    def _validate_from_data(self, picking_id, qty_by_prod):
        # create partial delivery by validating picking move line
        # with qty for product taken from the buffer
        partial_datas = {}
        picking = self.browse(picking_id)
        origin, dest = '', ''
        for move in picking.move_lines:
            origin = move.location_id.id
            dest = move.location_dest_id.id
            if move.state in ('draft', 'waitting', 'confirmed', 'assigned') \
                    and qty_by_prod.get(move.product_id.id):
                # delivery qty >= expected qty
                if qty_by_prod[move.product_id.id] >= move.product_qty:
                    partial_datas["move" + str(move.id)] = {
                        'product_qty': move.product_qty,
                        'product_uom': move.product_uom.id
                    }
                    qty_by_prod[move.product_id.id] -= move.product_qty
                else:
                    partial_datas["move" + str(move.id)] = {
                        'product_qty': qty_by_prod[move.product_id.id],
                        'product_uom': move.product_uom.id}
                    qty_by_prod[move.product_id.id] = 0
        # Check if still some products in the buffer
        for item in qty_by_prod:
            if qty_by_prod[item] > 0:
                # move in are validated automatically
                if picking.type in ['in', 'internal']:
                    product_details = self.pool['product.product'].read(
                        [item], ['uom_id', 'name'])[0]
                    # use read instead of building a uom dict in
                    # for movelines because extra product
                    # can be in no planned move
                    move_to_create = {
                        "name": "EXTRA DELIVERY : " + str(item) + " : " +
                        product_details['name'],
                        "date": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "date_expected": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "product_id": item,
                        "product_qty": qty_by_prod[item],
                        "product_uom": product_details['uom_id'][0],
                        "location_id": origin,
                        "location_dest_id": dest,
                        "picking_id": picking.id,
                        "company_id": picking.company_id.id}
                    move_id = self.pool['stock.move'].create(move_to_create)
                    partial_datas["move" + str(move_id)] = {
                        'product_qty': qty_by_prod[item],
                        'product_uom': move.product_uom.id}
                # move out raise an alert
                else:
                    raise models.except_models(
                        _('Warning !'),
                        _("Too much product delivered for picking '%s' (id %s)"
                          % (picking.name, picking.id)))
        self.do_partial([picking.id], partial_datas)
        return True
