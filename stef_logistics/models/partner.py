# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    stef_partner_id_string = fields.Char(
        string='Stef ref',
        help="Reference du partenaire chez Stef utilisé pour "
             "se connecter à l'EDI")
