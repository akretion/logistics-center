# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
from datetime import datetime
from collections import defaultdict

from odoo.addons.logistics_center.models.logistics import Logistic

from .common import (LogisticDialect, DATE_FORMATS)
from ..data.flow_delivery_manual import portal_delivery_head

_logger = logging.getLogger(__name__)


class Stef(Logistic):

    # Used with csv, then not for this provider
    _dialect = LogisticDialect()

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == 'stef'

    def __init__(self, *args, **kwargs):
        "It fails if no __init__"

    def run_flow(self, flow):
        # TODO move to Logistic class ?
        if flow.direction == 'export':
            records = flow._get_records_to_process()
            if records:
                return self._get_data_to_export(
                    records, flow, type='build_your_own')
            else:
                # TODO move to backend
                body = "No data to export with flow '%s'" % flow.name
                flow.logistics_backend_id.message_post(body=body)

    def _get_domain(self, flow):
        domain = [
            ('state', '=', flow.picking_state),
            ('logistics_blocked', '=', False),
            ('log_out_file_doc_id', '=', False)
        ]
        if flow.flow == 'delivery':
            domain.extend([
                ('picking_type_id.code', '=', 'outgoing'),
                ('picking_type_id.warehouse_id',
                    '=', flow.logistics_backend_id.warehouse_id.id),
            ])
        elif flow.flow == 'incoming':
            domain.extend([
                ('picking_type_id.code', '=', 'internal'),
                ('picking_type_id', '=', flow.env.ref(
                    'stef_logistics.stef_picking_type').id),
            ])
        else:
            _logger.warning("No matching records for flow '%s'" % flow.name)
            return [('id', '=', -1)]
        return domain

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
        return date.strftime('%Y%M')

    def _get_default_value(self, field):
        res = ''
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

    def _format_incoming_header(self, mapping):
        return """%(del_ord)s;;;;;;
%(cmdcli)s;;;;;;
%(trsdst)s;;;;;;
%(dat_drop)s;%(datliv)s;;;;;
;;;;;;
alias produit;type ul;réf lot;qté;poids;date rotation;référence palette client""" % mapping

    def _format_incoming_body(self, mapping):
        return "%(codprd)s;C1;%(num_lot)s;%(qty)s;%(weight)s;%(rotation)s" \
               ";;%(palette)s" % mapping

    def _format_delivery_header(self, mapping):
        return """%(del_ord)s;;;;;;
%(cmdcli)s;;;;;;
%(trsdst)s;;;;;;
%(dat_drop)s;%(datliv)s;;;;;
;;;;;;
alias produit;type ul;réf lot;qté;poids;date rotation;référence palette client""" % mapping

    def _format_delivery_body(self, mapping):
        return "%(codprd)s;C1;%(num_lot)s;%(qty)s;%(weight)s;%(rotation)s" \
               ";%(palette)s" % mapping

    def _prepare_head_data(self, picking, flow, delivery_head):
        settings = picking.picking_type_id.warehouse_id.logistics_id. \
            _logistics_center_settings()
        if flow.logistics_backend_id.version == 'stef-portail':
            res = {
                'del_ord': picking.name,
                'cmdcli': picking.origin or '',
                'trsdst': (
                    picking.company_id.partner_id and picking.company_id.
                    partner_id.stef_partner_id_string or ''),
                'datliv': self._convert_date(
                    picking.scheduled_date, 'datliv', delivery_head),
                'dat_drop': self._convert_date(
                    picking.drop_date, 'dat_drop', delivery_head)
            }
            if not res['dat_drop']:
                res['dat_drop'] = res['datliv']
            if flow.flow == "delivery":
                res["trsdst"] = picking.partner_id.stef_partner_id_string or ''
            return res
        else:
            # Real EDI: not implemented
            return {
                'codenr': 'E',
                'cmdcli': picking.name,
                'nomdos': settings['nomdos'],
                'codgln': settings['codgln'],
                'datliv': self._convert_date(
                    picking.scheduled_date, 'datliv', delivery_head),
                'trsdst': picking.partner_id.stef_partner_id_string,
            }

    def _prepare_line_data(self, move, flow):
        if flow.logistics_backend_id.version == 'stef-portail':
            return {
                'codprd': move.product_id.default_code,
                'type_ul': 'C1',
                'num_lot': hasattr(move, 'lot_id') and move.lot_id.name or "",
                'qty': move.product_uom_qty,
                'weight': move.product_id.weight * move.product_uom_qty,
                'rotation': '',
                'sscc': '',
                'palette': '',
            }
        else:
            # Real EDI: not implemented
            return {
                'codenr': 'L',
                'cmdcli': move.picking_id.name,
                'numlig': move.id,
                'codprd': move.product_id.default_code,
                'qliuc': move.product_uom_qty,
            }

    def build_your_own(self, records, flow):
        """ Here we don't use a csv format but a specific format
        """
        if flow.direction == 'export':
            data, issue = self._export_flow(records, flow)
        elif flow.direction == 'import':
            return NotImplementedError
        if data:
            return ('\n'.join(data), issue)
        else:
            _logger.info(" >>> no data to export")
            return (False, False)

    def _export_flow(self, pickings, flow):
        data = []
        for picking in pickings:
            exceptions = defaultdict(dict)
            # head_data, line_data = self._guess_dict_data(flow)
            vals = self._prepare_head_data(picking, flow, portal_delivery_head)
            # exceptions.update(self._check_field_length(
            #     vals, head_data, 'head'))
            data.append(
                getattr(self, '_format_%s_header' % flow.flow)(vals))
            if flow.flow == "delivery":
                for move in picking.move_lines:
                    vals = self._prepare_line_data(move, flow)
                    data.append(
                        getattr(self, '_format_%s_body' % flow.flow)(vals))
            elif flow.flow == "incoming":
                for move in picking.move_line_ids_without_package:
                    vals = self._prepare_line_data(move, flow)
                    data.append(
                        getattr(self, '_format_%s_body' % flow.flow)(vals))
            if exceptions:
                # Not used in this connector
                self._notify_exceptions(picking, exceptions)
            elif data:
                picking.write({'logistics_exception': False})
                _logger.info(" >>> ADD %s data" % flow.name)
            data.append('###;;;;;;')
        return (data, False)

    def _notify_exceptions(self, browse, exceptions, values=None, model=None):
        """ TODO refactor
        """
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

    def _get_portal_url(self):
        return 'http://www.edifresh.com/modules/wmsweb/index.php'
