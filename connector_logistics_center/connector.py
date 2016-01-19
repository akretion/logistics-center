# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
from openerp.addons.connector.connector import (install_in_connector)

install_in_connector()


class logistic_binding(orm.AbstractModel):
    """ Abstract Model for the Bindings.

    All the models used as bindings between Logistic and OpenERP
    (``logistic.res.partner``, ``logistic.product.product``, ...) should
    ``_inherit`` it.
    """
    _name = 'logistic.binding'
    _inherit = 'external.binding'
    _description = 'Logistic Binding (abstract)'

    _columns = {
        'backend_id': fields.many2one(
            'logistic.backend',
            'Logistic Backend',
            required=True,
            ondelete='restrict'),
        # some logistics center may not use it
        'logistic_id': fields.char('ID on Logistic center'),
    }

    # the _sql_contraints cannot be there due to this bug:
    # https://bugs.launchpad.net/openobject-server/+bug/1151703

