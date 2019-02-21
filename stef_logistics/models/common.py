# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from csv import Dialect, QUOTE_NONE


BACKEND_VERSION = '1.1'
BACKEND_VERSION_NAME = 'stef'
ENCODING = 'utf-8'

DATE_FORMATS = {
    'D1': '%Y%M%D',
    'D2': '%Y%M%D%H%m',
    'D3': '%y%M%D',
    'D4': '%H%m',
}


class LogisticDialect(Dialect):
    """Describe the usual properties of CSV files."""
    delimiter = ';'
    escapechar = '\\'
    quotechar = '"'
    doublequote = True
    quoting = QUOTE_NONE
    skipinitialspace = False
    lineterminator = '\n'
