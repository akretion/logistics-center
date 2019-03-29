# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

FLOWS = {
    'export_delivery_order':
        {'external_name': 'delivery_order',
         'sequence': 70},
    'export_incoming_shipment':
        {'external_name': 'receive_order',
         'sequence': 100}
}

READY_PICKING_STATE = ('confirmed', 'assigned')


def sanitize(string):
    "Make string compatible with stef files"
    if isinstance(string, (str)):
        if '\n' in string:
            # \n can't be in string because there is
            # QUOTING_NONE in csv dialect
            string = string.replace('\n', ',')
        if ';' in string:
            # ; is the delimiter and must not be in string
            string = string.replace(';', ',')
    else:
        string = ''
    return string


class LogisticsBackend(models.Model):
    _inherit = 'logistics.backend'

    version = fields.Selection(
        selection_add=[
            ('stef-portail', 'Stef portail'),
            ('stef-edi1.1', 'Stef EDI')])

    def delivery_order2export(self, last_exe_date):
        if not self.last_logistics_date:
            raise UserError(_("You must set 'Last export date' field"))
        picking_m = self.env['stock.picking']
        pickings = picking_m.search(self._get_delivery_order_domain())
        if pickings:
            kwargs = self._get_data_to_export(
                pickings, 'export_delivery_order',
                FLOWS['export_delivery_order'],
                self.version, type='build_your_own')
            self._tmp_create_file(kwargs)
            return kwargs
        return True

    def incoming_shipment2export(self, last_exe_date):
        return True
        incoming_sh_m = self.env['stock.picking']
        incomings = incoming_sh_m.search([
            ('state', 'in', READY_PICKING_STATE),
            ('type', '=', 'in'),
            ('logistics_blocked', '=', False),
            ('log_out_file_doc_id', '=', False),
            ('warehouse_id', '=', self.warehouse_id.id)])
        if incomings:
            kwargs = self._get_data_to_export(
                incomings, 'export_incoming_shipment',
                FLOWS['export_incoming_shipment'], self.version)
            return kwargs
        return True

    def _logistics_center_settings(self):
        return {
            'nomdos': 'LFG',
            'codgln': 999,  # code site 88B
        }
