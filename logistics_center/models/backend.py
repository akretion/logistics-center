# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import api, models, fields, _
from .logistics import get_logistics_parser


class LogisticsBackend(models.Model):
    _name = 'logistics.backend'
    _inherit = 'mail.thread'
    _description = "Logistics Backend to manage data exchange " \
                   "with logistics center"

    LOGISTIC_DEBUG = False

    name = fields.Char('Name', required=True)
    code = fields.Char(required=True, readonly=True)
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
    logistics_flow_ids = fields.One2many(
        comodel_name='logistics.flow', inverse_name='logistics_backend_id',
        string='Logistics flows', help="Logistics tasks flow")

    _sql_constraints = [
        ('operation_uniq_warehouse', 'unique(warehouse_id)',
         "Warehouse must be only used in only one Logistics Backend"),
    ]

    def delivery_order2export(self, *args, **kwargs):
        return NotImplementedError

    def button_logistics_portal(self):
        self.ensure_one()
        logistics = get_logistics_parser(self.code)
        return {
            'type': 'ir.actions.act_url',
            'url': logistics._get_portal_url(),
            'target': '_new',
        }

    def export_catalog(self, *args, **kwargs):
        return NotImplementedError

    def incoming_shipment2export(self, *args, **kwargs):
        return NotImplementedError

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
