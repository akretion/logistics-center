# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LogisticsBackend(models.Model):
    _inherit = 'logistics.backend'

    version = fields.Selection(
        selection_add=[
            ('stef-portail', 'Stef portail'),
            ('stef-edi1.1', 'Stef EDI')])

    def _logistics_center_settings(self):
        # only required for EDI
        return {
            'nomdos': 'LFG',
            'codgln': 999,  # code site 88B
        }
