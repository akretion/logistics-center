# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################


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
