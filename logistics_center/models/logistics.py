# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from csv import register_dialect, writer as csv_writer
from io import StringIO

from odoo import models, _


_logger = logging.getLogger(__name__)


class Logistic(object):
    """
    Generic abstract class for defining parser for different files and
    format to import. Inherit from it to create your
    own. If your file is a .csv or .xls format, you should consider inherit
    from the FileParser instead.
    """
    _dialect = None         # csv dialect

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

    def _check_logistics_data(self, *args, **kwargs):
        "Write or Create on Products with logistics product comes here"
        pass

    def _build_csv(self, records, method, encoding='utf-8'):
        register_dialect("logistics_dialect", self._dialect)
        csv_file = StringIO()
        writer = csv_writer(csv_file, dialect=self._dialect)
        non_compliants = []
        res = getattr(self, method)(records, writer, non_compliants)
        if res:
            csv_file.seek(0)
            return (csv_file.read(), non_compliants)
            _logger.info("\nStart to read datas to put file "
                         "for the method '%s'" % method)
        else:
            return (False, non_compliants)


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


def get_logistics_parser(parser_name, *args, **kwargs):
    """
    Return an instance of the good parser class base on the providen name
    :param char: parser_name
    :return: class instance of parser_name providen.
    """
    for cls in itersubclasses(Logistic):
        if cls.parser_for(parser_name):
            return cls(parser_name, *args, **kwargs)
    raise ValueError


class AbstractLogisticsFlow(models.AbstractModel):
    _name = 'abstract.logistics.flow'
    _description = 'Logistics Flow features'

    WAREHOUSE_LOGISTIC_EXCEPTION = _(
        "The warehouse '%s' have a wrong settings "
        " in 'Location Stock' or 'Location Input'")

    def get_logistics(self):
        """ 'logistics_center' field is not a m2o because it must be a required
        field but may be with no external logistics center : for internal use
        """
        res = []
        res.append(('internal', 'Internal'))
        log_m = self.pool['logistics.backend']
        log_backend_ids = log_m.search([])
        for log in log_m.browse(log_backend_ids):
            res.append((str(log.id), log.name))
        return res

    def _get_logistics(self):
        return self.get_logistics()
