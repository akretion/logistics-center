# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier camptocamp
#     @author David BEAL <david.beal@akretion.com>
#     @author Sebastien BEAU <sebastien.beau@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
        # some logistic center may not use it
        'logistic_id': fields.char('ID on Logistic center'),
    }

    # the _sql_contraints cannot be there due to this bug:
    # https://bugs.launchpad.net/openobject-server/+bug/1151703

