# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    logistics_id = fields.Many2one(
        comodel_name='logistics.backend',
        string='Logistics',
        compute='_compute_logistics_backend')

    def _compute_logistics_backend(self):
        self.ensure_one()
        self.logistics_id = self.env['logistics.backend'].search(
            [('warehouse_id', '=', self.id)])
