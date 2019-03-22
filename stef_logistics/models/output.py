# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import json
import logging
from datetime import datetime
from collections import defaultdict

from odoo.addons.logistics_center.models.logistics import Logistic

from .common import (
    LogisticDialect, DATE_FORMATS, BACKEND_VERSION)

FLOW_TYPE = 'manual'

if FLOW_TYPE == 'manual':
    from ..data.flow_delivery_manual import delivery_head, delivery_line
    from ..data.flow_incoming_manual import incoming_head, incoming_line
else:
    from ..data.flow_delivery import delivery_head, delivery_line
    from ..data.flow_incoming import incoming_head, incoming_line

_logger = logging.getLogger(__name__)

FLOWS = {
    'export_delivery_order':
        {'external_name': 'delivery_order', 'sequence': 70},
    'export_incoming_shipment':
        {'external_name': 'receive_order', 'sequence': 100}
}

READY_PICKING_STATE = ('waiting', 'confirmed', 'assigned')


def sanitize(string):
    "Make string compatible with stef files"
    if isinstance(string, (str)):
        if '\n' in string:
            # \n can't be in string because there is
            # QUOTING_NONE in csv dialect
            string = string.replace('\n', ',')
        if ';' in string:
            # ; is the delimiter and must not be in string
            string = string.replace(';', ',')
    else:
        string = ''
    return string


class Stef(Logistic):
    FROM_SITE_ID = 'FROM_SITE_ID'  # stef info
    CLIENT_ID = 'CLIENT_ID'        # stef info
    LOGIS_DATE = '%Y%M'

    _dialect = LogisticDialect()

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == BACKEND_VERSION

    def __init__(self, *args, **kwargs):
        "It fails if no __init__"

    def _convert_date(self, date, keydate=None, formats=None):
        if not date:
            return ''
        if isinstance(date, datetime):
            date = date.date()
        if keydate and formats:
            attrs = [x for x in formats if x.get('col') == keydate]
            attrs = attrs and attrs[0] or {}
            if attrs.get('type') in DATE_FORMATS.keys():
                return date.strftime(DATE_FORMATS[attrs['type']])
        return date.strftime(self.LOGIS_DATE)

    def _get_allowed_values(self, allowed):
        """Allowed comes stef data"""
        res = []
        if allowed.strip() in ['Upper Case', 'Mixed Case']:
            res.append('')
        elif allowed == self.LOGIS_DATE:
            res = ''
        elif '|' in allowed:
            res = [re.sub("[.!,;' ]", '', elm) for elm in allowed.split('|')]
        else:
            res.append(re.sub("[.!,;' ]", '', allowed))
        return res

    def _get_default_value(self, field):
        res = ''
        # alloweds = self._get_allowed_values(field['allowed'])
        alloweds = field.get('allowed')
        default = field.get('def')
        res = default
        if alloweds and default not in alloweds:
            res = ''    # stef requirements
        return res

    def _get_values(self, main_values, definition_fields):
        """
        :param main_values: e.g.
            {'codenr': 'E', 'cmdcli': 'STF/OUT/1', 'nomdos': 'LFG',
             'codgln': '??', 'datliv': '20190102/20/19', 'trsdst': False}
        :type main_values: :py:class:`Dict`
        :param definition_fields: e.g.
            [{'seq': 1, 'len': 5, 'type': 'A', 'col': 'codenr', 'req': True,
              'def': 'E', 'allowed': ['E'], 'comment': "bla"}, {...}]
        :type definition_fields: List of Dict
        :rtype: list
        """
        values = []
        main_keys = main_values.keys()
        for field in definition_fields:
            if field.get('col') in main_keys:
                values.append(main_values[field['col']])
            else:
                # TODO probably remove
                # values are determined by definition_fields
                values.append(self._get_default_value(field))
        return values

    def _format_delivery_header(self, mapping):
        return """%(del_ord)s;;;;;;

%(cmdcli)s;;;;;;

%(trsdst)s;;;;;;

%(dat_drop)s;%(datliv)s;;;;;

;;;;;;

alias produit;type ul;réf lot;qté;poids;date rotation;référence palette client
""" % mapping

    def _format_delivery_body(self, mapping):
        return "%(codprd)s;C1;%(num_lot)s;%(qty)s;%(weight)s;%(rotation)s" \
               ";%(palette)s" % mapping

    def _prepare_incoming(self, picking, incoming_head):
        return {
        }

    def _prepare_incoming_line(self, move, incoming_line):
        return {
        }

    def _prepare_picking(self, picking, delivery_head):
        settings = picking.picking_type_id.warehouse_id.logistics_id. \
            _logistics_center_settings()
        if FLOW_TYPE == 'manual':
            res = {
                'del_ord': picking.name,
                'cmdcli': picking.origin,
                'trsdst': picking.partner_id.stef_partner_id_string or '',
                'datliv': self._convert_date(
                    picking.scheduled_date, 'datliv', delivery_head),
                'dat_drop': self._convert_date(
                    picking.drop_date, 'dat_drop', delivery_head)
            }
            if not res['dat_drop']:
                res['dat_drop'] = res['datliv']
            return res
        else:
            return {
                'codenr': 'E',
                'cmdcli': sanitize(picking.name),
                'nomdos': settings['nomdos'],
                'codgln': settings['codgln'],
                'datliv': self._convert_date(
                    picking.scheduled_date, 'datliv', delivery_head),
                'trsdst': picking.partner_id.stef_partner_id_string,
            }

    def _prepare_move(self, move, delivery_line):
        if FLOW_TYPE == 'manual':
            return {
                'codprd': move.product_id.default_code,
                'type_ul': 'C1',
                'num_lot': '',
                'qty': move.product_uom_qty,
                'weight': move.product_id.weight * move.product_uom_qty,
                'rotation': '',
                'palette': '',
            }
        else:
            return {
                'codenr': 'L',
                'cmdcli': move.picking_id.name,
                'numlig': move.id,
                'codprd': move.product_id.default_code,
                'qliuc': move.product_uom_qty,
            }

    def _should_i_set_header(self, backend):
        return True

    def _check_field_length(self, vals, flow, flow_name=None):
        "Check if data doesn't overcome the length of the field"
        exceptions = {}
        for field in flow:
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
                    key = flow_name or '_'
                    exceptions.update({key: {fname: {
                        'data': vals[fname],
                        'max_length': field.get('len')}}})
        return exceptions

    def _check_logistics_data(self, browse):
        pass

    def _build_your_own(self, records, method):
        """ Here we don't use a csv format but a specific format
        """
        data = getattr(self, method)(records)
        if data:
            _logger.info(" >>> 'export_delivery_order' ADD picking data")
            return ('\n'.join(data), False)
        else:
            _logger.info(" >>> 'export_delivery_order' no data to export")
            return (False, False)

    def export_delivery_order(self, pickings):
        data = []
        for picking in pickings:
            exceptions = defaultdict(dict)
            vals = self._prepare_picking(picking, delivery_head)
            exceptions.update(self._check_field_length(
                vals, delivery_head, 'head'))
            data.append(self._format_delivery_header(vals))
            for move in picking.move_lines:
                # if move.state in ['assigned']:
                vals = self._prepare_move(move, delivery_line)
                exceptions.update(
                    self._check_field_length(vals, delivery_line, 'line'))
                data.append(self._format_delivery_body(vals))
            if exceptions:
                self._notify_exceptions(
                    picking, exceptions, model='stock.picking')
            elif data:
                picking.write({'logistics_exception': False})
            data.append('###')
        return data

    def export_incoming_shipment(self, pickings, writer, non_compliants):
        data_to_send = False
        header, backend = self._should_i_set_header(pickings[0])
        for picking in pickings:
            data = []
            exceptions = defaultdict(dict)
            if header:
                backend.set_header_file(writer, 'MASTER', incoming_head)
            vals = self._prepare_incoming(picking, incoming_head)
            exceptions.update(self._check_field_length(
                vals, incoming_head, 'head'))
            data.append(self._get_values(vals, incoming_head))
            for move in picking.move_lines:
                if header:
                    backend.set_header_file(writer, 'RELATED', incoming_line)
                # if move.state in ['assigned']:
                vals = self._prepare_incoming_line(move, incoming_line)
                exceptions.update(
                    self._check_field_length(vals, incoming_line, 'line'))
                data.append(self._get_values(vals, incoming_line))
            if exceptions:
                self._notify_exceptions(picking, exceptions,
                                        model='stock.picking')
                non_compliants.append(picking)
            elif data:
                picking.write({'logistics_exception': False})
                data_to_send = True
                for elm in data:
                    writer.writerow(elm)
        if data_to_send:
            _logger.info(" >>> 'export_incoming_shipment' ADD incoming data")
            return True
        else:
            _logger.info(" >>> 'export_incoming_shipment' no data")
            return False

    def _notify_exceptions(self, browse, exceptions, values=None, model=None):
        mess_vals = {
            'subject': "stef exceptions: Too wide data",
            'body': "Here is problematic keys <br/>\n%s"
                    % json.dumps(exceptions),
            'model': model or browse._name,
            'res_id': browse.id,
            'type': 'notification'}
        browse._model.env['mail.message'].create(
            browse._cr, browse._uid, mess_vals, context=browse._context)
        if values:
            values['logistics_exception'] = True
