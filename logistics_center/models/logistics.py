# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
from datetime import datetime
from csv import register_dialect, writer as csv_writer
from io import StringIO

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

    def run_flow(self, flow):
        return NotImplementedError

    def check_logistics_data(self, *args, **kwargs):
        "Write or Create on Products with logistics product comes here"
        return NotImplementedError

    def build_csv(self, records, method, encoding='utf-8'):
        register_dialect("logistics_dialect", self._dialect)
        csv_file = StringIO()
        writer = csv_writer(csv_file, dialect=self._dialect)
        issue = []
        res = getattr(self, method)(records, writer, issue)
        if res:
            csv_file.seek(0)
            return (csv_file.read(), issue)
            _logger.info("\nStart to read datas to put file "
                         "for the method '%s'" % method)
        else:
            return (False, issue)

    def build_your_own(self, *args, **kwargs):
        """ If your files are not csv, you may define your own format
        """
        return NotImplementedError

    def import_data(self, *args, **kwargs):
        """ """
        return NotImplementedError

    def _get_data_to_export(self, records, flow, type='csv'):
        if type == 'csv':
            file_data, issue = self.build_csv(records, flow)
        else:
            file_data, issue = self.build_your_own(records, flow)
        if issue:
            # some records are not compliant with logistics specs
            # they shouldn't be taken account
            records = set(records) - set(issue)
            issue.write({'logistics_exception': True})
            mess = "Error when playing flow '%s' from Logistics center '%s"
            issue.message_post(body=mess % (
                flow.name, flow.logistics_backend_id.name))
        if file_data:
            self.amend_file_data(flow, file_data)
            return self.prepare_doc_vals(file_data, records, flow)

    def amend_file_data(self, flow, file_data):
        """ You may modify your file before store it
        """
        return NotImplementedError

    def prepare_doc_vals(self, file_data, records, flow):
        """ You may inherit this method to override these values """
        vals = {}
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        back_name = flow.logistics_backend_id.code
        vals = {
            'file_datas': base64.b64encode(file_data.encode('utf-8')),
            'name': '%s %s %s' % (back_name, flow.flow, now),
            'active': True,
            'datas_fname': '%s_%s.csv' % (back_name, now),
            # send records impacted by data exportation
            'records': records}
        return vals

    def sanitize(string):
        """ Some chars may be forbidden by your Logistics center
            Implements your own rules"""
        return NotImplementedError

    def _get_portal_url(self):
        """ Used by button on backend to access Logistics website
        """
        return NotImplementedError

    def _check_field_length_helper(self, vals, field_def, name='_'):
        """ Check if data doesn't overcome the length of the field
            Use only if you need
            Provided field_def must be in the form:
            {'seq': 4, 'len': 6, 'type': 'I', 'col': 'qty',
             'req': True, 'comment': "qté"},
             return Exception dict
        """
        # TODO improve or remove
        exceptions = {}
        for field in field_def:
            to_collect = False
            fname = field.get('col')
            if vals.get(fname):
                if field.get('type') in ('I') and field.get('len'):
                    try:
                        if vals[fname] > int('9' * field.get('len')):
                            to_collect = True
                    except Exception as e:
                        _logger.warning(
                            "Field length bug with key '%s' value '%s'\n%s" % (
                                fname, vals[fname], e))
                if field.get('type') in ('A') and field.get('len'):
                    try:
                        if len(vals[fname]) > field.get('len'):
                            to_collect = True
                    except Exception as e:
                        _logger.warning(
                            "Field length bug with key '%s' value '%s'\n%s" % (
                                fname, vals[fname], e))
                if to_collect:
                    exceptions.update({name: {fname: {
                        'data': vals[fname],
                        'max_length': field.get('len')}}})
        return exceptions


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
