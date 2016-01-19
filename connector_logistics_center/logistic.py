# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from _csv import register_dialect
import unicodecsv
from cStringIO import StringIO
import base64
from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import orm, fields
from .connector import logistic_binding


_logger = logging.getLogger(__name__)


class Logistic(object):
    """
    Generic abstract class for defining parser for different files and
    format to import in a bank statement. Inherit from it to create your
    own. If your file is a .csv or .xls format, you should consider inherit
    from the FileParser instead.
    """
    _dialect = None         # csv dialect
    DEBUG_FIELD_REQUIRED_MARK = '/!\\'

    @classmethod
    def parser_for(cls, parser_name):
        """
        Override this method for every new logistics center
        return the good class from his name.
        """
        return False

    def export_delivery_order(self, *args, **kwargs):
        return NotImplementedError

    def export_catalog(self, *args, **kwargs):
        return NotImplementedError

    def export_incoming_shipment(self, *args, **kwargs):
        return NotImplementedError

    def build_csv(self, browse_object, method, encoding='utf-8'):
        register_dialect("logistic_dialect", self._dialect)
        csv_file = StringIO()
        # https://github.com/jdunck/python-unicodecsv
        writer = unicodecsv.writer(csv_file, encoding=encoding,
                                   dialect=self._dialect)
        res = getattr(self, method)(browse_object, writer)
        if res:
            csv_file.seek(0)
            return csv_file.read()
            _logger.info("\nStart to read datas to put file "
                         "for the method '%s'" % method)
        else:
            return False


def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def get_logistic_parser(parser_name, *args, **kwargs):
    """
    Return an instance of the good parser class base on the providen name
    :param char: parser_name
    :return: class instance of parser_name providen.
    """
    for cls in itersubclasses(Logistic):
        if cls.parser_for(parser_name):
            return cls(parser_name, *args, **kwargs)
    raise ValueError


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'logistic_bind_ids': fields.one2many(
            'logistic.product.product',
            'openerp_id',
            string='Logistic Bindings',),
    }


class LogisticsProductProduct(orm.Model):
    _name = 'logistic.product.product'
    _description = "Logistics product"
    _inherit = 'logistic.binding'

    _columns = {
        'openerp_id': fields.many2one(
            'product.product',
            string='Product',
            ondelete='cascade'),
    }

    _sql_constraints = [
        ('logistic_uniq', 'unique(backend_id, openerp_id)',
         "Logistics Backend with the same id already exists on this product: "
         "must be unique"),
    ]


class LogisticBackend(orm.Model):
    _name = 'logistic.backend'
    _description = 'Logistics Backend'

    _inherit = 'connector.backend'
    _inherits = {'file.repository': 'file_repository_id'}

    _backend_type = 'logistic'

    LOGISTIC_DEBUG = False

    def select_versions(self, cr, uid, context=None):
        """ Available versions
        Can be inherited to add custom versions.
        """
        return []

    def _select_versions(self, cr, uid, context=None):
        return self.select_versions(cr, uid, context=context)

    def export_delivery_order(self, *args, **kwargs):
        return NotImplementedError

    def export_catalog(self, *args, **kwargs):
        return NotImplementedError

    def export_incoming_shipment(self, *args, **kwargs):
        return NotImplementedError

    def onchange_repository(self, cr, uid, ids, repository, context=None):
        name = self.pool['file.repository'].browse(cr, uid, repository,
                                                   context=context).name
        return {'value': {'name': name}}

    _columns = {
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True,
            help="Version must be added by modules dealing with "
            "logistics center synchronization. Install one of these"),
        'name': fields.char('Name', size=32),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',),
        'file_repository_id': fields.many2one(
            'file.repository',
            'Repository',
            required=True,
            ondelete="cascade",
            help="Define connection with external external location"),
        'warehouse_id': fields.many2one(
            'stock.warehouse',
            'Warehouse',
            required=True,
            ondelete="cascade",
            help="Warehouse of the logistics center"),
    }

    _sql_constraints = [
        ('file_repository_id_uniq', 'unique(file_repository_id)',
         "'File repository' with the same ID already exists : must be unique"),
    ]

    def get_product_ids(
            self, cr, uid, backend_id, last_exe_date, context=None):
        date_clause = ''
        if last_exe_date:
            date_clause = "AND 'update_date' > '%s'" % last_exe_date
        query = """
SELECT GREATEST (pt.write_date, pp.write_date) AS update_date, pp.id AS id
FROM product_template pt LEFT JOIN product_product pp
    ON pp.product_tmpl_id = pt.id
    LEFT JOIN logistic_product_product log
        ON log.openerp_id = pp.id
WHERE log.backend_id = %(backend_id)s
    %(date_clause)s
ORDER BY pp.default_code ASC """ % {'backend_id': backend_id,
                                    'date_clause': date_clause, }
        cr.execute(query)
        return [id for date, id in cr.fetchall()]

    def _prepare_doc_vals(
            self, cr, uid, backend_version, file_datas, model_ids,
            flow, context=None):
        "You may inherit this method to override these values"
        vals = {}
        now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
        name = '%s %s %s' \
            % (backend_version.capitalize(), flow['external_name'], now)
        vals = {
            'file_datas': base64.b64encode(file_datas),
            'name': name,
            'active': True,
            'sequence': flow['sequence'],
            'datas_fname': '%s_%s.csv' % (flow['external_name'], now),
            # send record ids impacted by datas exportation
            'ids_from_model': model_ids}
        return vals

    def get_datas_to_export(
            self, cr, uid, backend_ids, model, model_ids,
            export_method, flow, backend_version, context=None):
        assert len(backend_ids) == 1, "Will only take one resource id"
        backend = self.browse(cr, uid, backend_ids[0], context=context)
        logistic = get_logistic_parser(backend.version)
        browse = model.browse(cr, uid, model_ids, context=context)
        file_datas = logistic.build_csv(browse, export_method)
        if file_datas:
            return self._prepare_doc_vals(cr, uid, backend_version, file_datas,
                                          model_ids, flow, context=context)
        else:
            raise orm.except_orm("Error in '%s': " % export_method,
                                 "Check backend '%s' with \n%s ids %s, "
                                 "there is no data to put in file, "
                                 % (backend.name, model._name, model_ids))

    def logistic_debug_mode(self, cr, uid, ids, context=None):
        "Implement in your logistics center module"
        return


class AbstractLogisticsFlow(orm.AbstractModel):
    _name = 'abstract.logistic.flow'

    WAREHOUSE_LOGISTIC_EXCEPTION = _(
        "The warehouse '%s' have a wrong settings "
        " in 'Location Stock' or 'Location Input'")

    def get_logistic(self, cr, uid, context=None):
        """ 'logistic_center' field is not a m2o because it must be a required
        field but may be with no external logistics center : for internal use
        """
        res = []
        res.append(('internal', 'Internal'))
        log_m = self.pool['logistic.backend']
        log_backend_ids = log_m.search(cr, uid, [], context=context)
        for log in log_m.browse(cr, uid, log_backend_ids, context=context):
            res.append((str(log.id), log.name))
        return res

    def _get_logistic(self, cr, uid, context=None):
        return self.get_logistic(cr, uid, context=context)

    _columns = {
        'logistic_center': fields.selection(
            _get_logistic,
            string='Logistics Center',
            required=True,
            oldname="logistic",
            help="Logistics center choosen to deliver the order"),
    }

    def get_logistic_backend(self, cr, uid, ids, origin='order', context=None):
        """return logistics backend id (if exists)
            according to sale/purchase order id"""
        assert len(ids) == 1, "Will only take one resource id"
        if origin == 'order':
            order = self.browse(cr, uid, ids[0], context=context)
            if order.logistic_center and order.logistic_center != 'internal':
                logistic_id = int(order.logistic_center)
                return self.pool['logistic.backend'].browse(
                    cr, uid, logistic_id, context=context)
            else:
                return False
        elif origin == 'warehouse':
            warehouse_id = ids[0]
            backend_m = self.pool['logistic.backend']
            warehouses = {}
            backend_ids = backend_m.search(cr, uid, [], context=None)
            for backend in backend_m.browse(cr, uid, list(set(backend_ids)),
                                            context=context):
                warehouses[backend.warehouse_id.id] = backend.id
            if warehouse_id in warehouses:
                return str(warehouses[warehouse_id])
            else:
                return 'internal'
        else:
            return False
