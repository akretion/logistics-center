# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from csv import Dialect, QUOTE_NONE

BACKEND_VERSION = 'stef-portail'
ENCODING = 'utf-8'

LOGISTICS_CODE = 'stef'
LOGISTICS_NAME = 'Stef'

DATE_FORMATS = {
    'D1': '%Y%M%D',
    'D2': '%Y%M%D%H%m',
    'D3': '%y%M%D',
    'D4': '%H%m',
    'D5': '%d/%m/%Y',
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
