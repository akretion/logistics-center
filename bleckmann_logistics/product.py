# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _check_default_code(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if ';' in obj.default_code or ' ' in obj.default_code:
            return False
        return True

    _constraints = [
        (_check_default_code,
         "\nSome chars are forbidden for Internal Reference:"
         "\n- Semi colon\n- Space",
         ['default_code'])
    ]

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)',
         "The Internal Reference must be unique in all companies"),
    ]
