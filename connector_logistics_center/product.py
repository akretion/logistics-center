# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        # Implement your method in your module to check if required
        'logistics_exception': fields.boolean(
            'Logistics Exception',
            help="Checked if a wrong data prevent you to send "
                 "the product to your logistics center"),
        'logistics_to_check': fields.boolean(
            string='Please click on the button Check Logistics'),
    }

    def check_logistics(self, cr, uid, ids, context=None):
        # TODO make it right with several ids
        assert len(ids) == 1, "Will only take one resource id"
        product = self.browse(cr, uid, ids, context=context)[0]
        for bind in product.logistic_bind_ids:
            # TODO make it right with several binds
            return bind.backend_id.check_data(product)
        return True

    def _require_logistics_check(self, cr, uid, vals, context=None):
        """Override according to your logistics center
           Typical override:
                vals['logistics_to_check'] = True
        """
        pass

    def write(self, cr, uid, ids, vals, context=None):
        self._require_logistics_check(cr, uid, vals, context=context)
        return super(ProductProduct, self).write(
            cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        vals['logistics_to_check'] = True
        return super(ProductProduct, self).create(
            cr, uid, vals, context=context)
