# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'sent_to_logistics': fields.boolean(
            'Sent To Logistics',
            help="Definition of the product has been submit to "
                 "Logistics center"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'defaut_code' in vals:
            immutable_code_products = []
            for product in self.browse(cr, uid, ids, context=context):
                if product.sent_to_logistics:
                    immutable_code_products.append(
                        (product.name, product.id))
            if immutable_code_products:
                raise orm.except_orm(
                    _('Internal Reference'),
                    _(self.default_code_alert()) % immutable_code_products)
        return super(ProductProduct, self).write(
            cr, uid, ids, vals, context=context)

    def default_code_alert(self):
        return _("Internal Reference of these products '%s' "
                 "can't be changed because it have been exchanged with "
                 "external partners.")
