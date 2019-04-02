# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from .common import (LOGISTICS_CODE, LOGISTICS_NAME)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    external_type = fields.Selection(
        string='External', selection=[(LOGISTICS_CODE, LOGISTICS_NAME)])
