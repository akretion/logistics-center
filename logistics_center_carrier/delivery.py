# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class LogisticsDeliveryCarrier(orm.Model):
    _name = 'logistics.delivery.carrier'
    _inherit = 'logistic.binding'
    _inherits = {'delivery.carrier': 'erp_id'}
    _description = 'Logistics center carriers'

    _columns = {
        'erp_id': fields.many2one(
            'delivery.carrier',
            string='Delivery carrier',
            required=True,
            ondelete='cascade'
        ),
        'name_ext': fields.char(
            'External name',
            size=64,
            required=True,
        ),
    }

    _sql_constraints = [
        ('logistic_uniq', 'unique(backend_id, name_ext)',
         _("A delivery carrier with the same name on this logistics center "
           "already exists.")),
    ]


class DeliveryCarrier(orm.Model):
    _inherit = "delivery.carrier"
    _columns = {
        'logistics_bind_ids': fields.one2many(
            'logistics.delivery.carrier',
            'erp_id',
            string='Logistics bindings',),
    }


class LogisticsBackend(orm.Model):
    _inherit = 'logistic.backend'

    _columns = {
        'logistics_carrier_ids': fields.one2many(
            'logistics.delivery.carrier',
            'backend_id',
            'Logistics carriers',),
    }
