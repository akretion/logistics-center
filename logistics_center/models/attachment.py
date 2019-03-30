# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    external_type = fields.Selection(
        string='External', selection=[])
    sending_date = fields.Datetime(
        string="Transmission Date",
        help="Date to which the file has been transmit "
             "to the logistics center")
