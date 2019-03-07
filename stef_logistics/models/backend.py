# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields

from .common import (BACKEND_VERSION, BACKEND_VERSION_NAME)

_logger = logging.getLogger(__name__)

FLOWS = {
    'export_delivery_order':
        {'external_name': 'delivery_order',
         'sequence': 70},
    'export_incoming_shipment':
        {'external_name': 'receive_order',
         'sequence': 100}
}

READY_PICKING_STATE = ('waiting', 'confirmed', 'assigned')


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
            (BACKEND_VERSION, '%s %s' % (
                BACKEND_VERSION_NAME, BACKEND_VERSION))])

    def _prepare_doc_vals(self, backend_version, file_datas, records, flow):
        return super(LogisticsBackend, self)._prepare_doc_vals(
            backend_version, file_datas, records, flow)

    def _tmp_create_file(self, kwargs):
        # {'records': stock.picking(1,),
        #  'file_datas': b'RTtTVEYvT1Vi4wCg==',
        #  'sequence': 70, 'name': '1.1 delivery_order 2019-02-21_15-49-10',
        #  'datas_fname': 'del_order_2019-02-21_15-49-10.csv', 'active': True}
        attach = self.env['ir.attachment'].create({
            'datas': kwargs['file_datas'],
            'name': kwargs['datas_fname'],
            'datas_fname': kwargs['datas_fname']})
        kwargs['records'].write({'log_out_file_doc_id': attach.id})

    def delivery_order2export(self, last_exe_date):
        picking_m = self.env['stock.picking']
        pickings = picking_m.search([
            ('state', 'in', READY_PICKING_STATE),
            ('picking_type_id.code', '=', 'outgoing'),
            ('picking_type_id.warehouse_id', '=', self.warehouse_id.id),
            ('logistics_blocked', '=', False),
            ('log_out_file_doc_id', '=', False)])
        if pickings:
            kwargs = self._get_data_to_export(
                pickings, 'export_delivery_order',
                FLOWS['export_delivery_order'], BACKEND_VERSION)
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
                FLOWS['export_incoming_shipment'], BACKEND_VERSION)
            return kwargs
        return True

    def _set_header_file(self, writer, header_type,
                         definition_fields):
        "Only used in debug mode to display header in csv file"
        pass

    def _logistics_center_settings(self):
        # pass
        return {
            'nomdos': 'LFG',
            'codgln': 999,  # code site 88B
        }
