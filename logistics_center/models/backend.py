# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import base64

from odoo import api, models, fields, _
from .logistics import get_logistics_parser


class LogisticsBackend(models.Model):
    _name = 'logistics.backend'
    _description = 'Logistics Backend'

    LOGISTIC_DEBUG = False

    name = fields.Char('Name', required=True)
    version = fields.Selection(
        selection=[],
        string='Version',
        help="Version must be added by modules dealing with "
             "logistics center synchronization. Install one of these")
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        ondelete="cascade",
        help="Warehouse of the logistics center")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        ondelete="cascade")

    _sql_constraints = [
        ('operation_uniq_per_product', 'unique(warehouse_id)',
         "Warehouse must be only used in only one Logistics Backend"),
    ]

    def delivery_order2export(self, *args, **kwargs):
        return NotImplementedError

    def export_catalog(self, *args, **kwargs):
        return NotImplementedError

    def incoming_shipment2export(self, *args, **kwargs):
        return NotImplementedError

    def _prepare_doc_vals(self, backend_version, file_datas, records, flow):
        "You may inherit this method to override these values"
        vals = {}
        now = fields.Datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = '%s %s %s' \
            % (backend_version.capitalize(), flow['external_name'], now)
        vals = {
            'file_datas': base64.b64encode(file_datas.encode('utf-8')),
            'name': name,
            'active': True,
            'sequence': flow['sequence'],
            'datas_fname': '%s_%s.csv' % (flow['external_name'], now),
            # send records impacted by data exportation
            'records': records}
        return vals

    def _get_data_to_export(
            self, records, export_method, flow, backend_version):
        self.ensure_one()
        logistics = get_logistics_parser(backend_version)
        file_datas, non_compliants = logistics._build_csv(
            records, export_method)
        model_ids = []
        if non_compliants:
            # some records are not compliant with logistics specs
            # they shouldn't be taken account
            records = set(records) - set(non_compliants)
            non_compliants.write({'logistics_exception': True})
        if file_datas:
            self._amend_file_data(file_datas)
            return self._prepare_doc_vals(
                backend_version, file_datas, records, flow)
        else:
            self.env.cr.commit()
            flow_title = "Error in '%s': " % export_method
            if model_ids:
                raise models.except_models(
                    flow_title,
                    "Check backend '%s' with \n%s ids %s, "
                    "there is no data to put in file, "
                    % (backend.name, model._name, model_ids))
            else:
                raise models.except_models(
                    flow_title,
                    "No compliant data to send with '%s' backend"
                    % backend.name)

    def _check_data(self, browse):
        "Allow to check"
        assert len(ids) == 1, "Will only take one resource id"
        # TODO manage case with several browse values
        # assert len(browse) == 1, (
        #     "Will only take one browse to check logistics data")
        backend = self.browse(ids)[0]
        logistics = get_logistics_parser(backend.version)
        return logistics.check_logistics_data(browse)

    def _amend_file_data(self, data):
        "Allow to modify data before to create file.document"
        pass

    def _logistics_debug_mode(self):
        "To implement in your logistics center module"
        return
