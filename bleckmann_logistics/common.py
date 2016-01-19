# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from csv import Dialect
from _csv import QUOTE_NONE


BACKEND_VERSION = 'bleckmann'
SKU_SUFFIX = '.OS'
ENCODING = 'utf-8'


class LogisticDialect(Dialect):
    """Describe the usual properties of CSV files."""
    delimiter = ';'
    escapechar = '\\'
    quotechar = '"'
    doublequote = True
    quoting = QUOTE_NONE
    skipinitialspace = False
    lineterminator = '\n'
