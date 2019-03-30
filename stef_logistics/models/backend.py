# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

READY_PICKING_STATE = ('confirmed', 'assigned')


class LogisticsBackend(models.Model):
    _inherit = 'logistics.backend'

    version = fields.Selection(
        selection_add=[
            ('stef-portail', 'Stef portail'),
            ('stef-edi1.1', 'Stef EDI')])

    # def incoming_shipment2export(self, last_exe_date):
    #     return True
    #     incoming_sh_m = self.env['stock.picking']
    #     incomings = incoming_sh_m.search([
    #         ('state', 'in', READY_PICKING_STATE),
    #         ('type', '=', 'in'),
    #         ('logistics_blocked', '=', False),
    #         ('log_out_file_doc_id', '=', False),
    #         ('warehouse_id', '=', self.warehouse_id.id)])
    #     if incomings:
    #         kwargs = self._get_data_to_export(
    #             incomings, 'export_incoming_shipment',
    #             FLOWS['export_incoming_shipment'], self.version)
    #         return kwargs
    #     return True

    def _logistics_center_settings(self):
        return {
            'nomdos': 'LFG',
            'codgln': 999,  # code site 88B
        }
