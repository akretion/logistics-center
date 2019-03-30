# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields
from .logistics import get_logistics_parser


class LogisticsBackend(models.Model):
    _name = 'logistics.backend'
    _inherit = 'mail.thread'
    _description = "Logistics Backend to manage data exchange " \
                   "with logistics center"

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

    def button_reload(self):
        pass

    def button_logistics_portal(self):
        self.ensure_one()
        logistics = get_logistics_parser(self.code)
        return {
            'type': 'ir.actions.act_url',
            'url': logistics._get_portal_url(),
            'target': '_new',
        }
