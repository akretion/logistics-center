# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import orm, fields


class LogisticBackend(orm.Model):
    _inherit = 'logistic.backend'

    _columns = {
        'warehouse_id': fields.property(
            'stock.warehouse',
            relation='stock.warehouse',
            string='Warehouse',
            type='many2one',
            required=True,
            ondelete="cascade",
            view_load=True,
            help="Warehouse of the logistics center"),
    }
