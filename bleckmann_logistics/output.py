# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import pycountry
import json
import logging
from collections import defaultdict

from openerp.osv import orm
from openerp.addons.connector_logistics_center.logistic import Logistic

from .common import LogisticDialect, BACKEND_VERSION, SKU_SUFFIX
from .data.flow_delivery import delivery_head, delivery_line
from .data.flow_sku import sku
from .data.flow_incoming import incoming_head, incoming_line

_logger = logging.getLogger(__name__)

FLOWS = {
    'export_catalog':
        {'external_name': 'sku',
         'sequence': 50},
    'export_delivery_order':
        {'external_name': 'delivery_order',
         'sequence': 70},
    'export_incoming_shipment':
        {'external_name': 'receive_order',
         'sequence': 100}
}


def sanitize(string):
    "Make string compatible with bleckmann files"
    if isinstance(string, (str, unicode)):
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


class LogisticBackend(orm.Model):
    _inherit = 'logistic.backend'

    def select_versions(self, cr, uid, context=None):
        """ Available versions
        """
        selected = super(LogisticBackend, self).select_versions(
            cr, uid, context=context)
        selected.append((BACKEND_VERSION, BACKEND_VERSION.capitalize()))
        return selected

    def _prepare_doc_vals(
            self, cr, uid, backend_version, file_datas, model_ids,
            flow, context=None):
        vals = super(LogisticBackend, self)._prepare_doc_vals(
            cr, uid, backend_version, file_datas, model_ids, flow,
            context=context)
        return vals

    def export_catalog(self, cr, uid, ids, last_exe_date, context=None):
        where_clause = " AND pp.default_code != ''"
        product_ids = self.get_product_ids(
            cr, uid, ids[0], last_exe_date, where_clause=where_clause,
            context=context)
        if product_ids:
            product_m = self.pool['product.product']
            to_immute_product_ids = product_m.search(
                cr, uid, [
                    ('sent_to_logistics', '=', False),
                    ('id', 'in', product_ids)], context=context)
            product_vals = {'sent_to_logistics': True}
            product_m.write(
                cr, uid, to_immute_product_ids, product_vals, context=context)
            kwargs = self.get_datas_to_export(
                cr, uid, ids, product_m, product_ids, 'export_catalog',
                FLOWS['export_catalog'], BACKEND_VERSION, context=context)
            return kwargs
        return True

    def export_delivery_order(self, cr, uid, ids, last_exe_date, context=None):
        picking_m = self.pool['stock.picking.out']
        picking_ids = picking_m.search(
            cr, uid, [
                ('state', 'in', ('assigned',)),
                ('type', '=', 'out'),
                ('logistics_blocked', '=', False),
                ('log_out_file_doc_id', '=', False),
                ('logistic_center', '=', str(ids[0])),
            ],
            context=context)
        if picking_ids:
            kwargs = self.get_datas_to_export(
                cr, uid, ids, picking_m, picking_ids, 'export_delivery_order',
                FLOWS['export_delivery_order'], BACKEND_VERSION,
                context=context)
            return kwargs
        return True

    def export_incoming_shipment(self, cr, uid, ids, last_exe_date,
                                 context=None):
        incoming_sh_m = self.pool['stock.picking']
        incoming_sh_ids = incoming_sh_m.search(
            cr, uid, [
                ('state', 'in', ('assigned',)),
                ('type', '=', 'in'),
                ('logistics_blocked', '=', False),
                ('log_out_file_doc_id', '=', False),
                ('logistic_center', '=', str(ids[0])),
            ],
            context=context)
        if incoming_sh_ids:
            kwargs = self.get_datas_to_export(
                cr, uid, ids, incoming_sh_m, incoming_sh_ids,
                'export_incoming_shipment', FLOWS['export_incoming_shipment'],
                BACKEND_VERSION, context=context)
            return kwargs
        return True

    def _amend_file_data(self, data):
        "Allow to modify data before to create file.document"
        # hack to manage weird behavior of unicode csv with \n chars
        data = data.replace('\\\n', '\n')

    def set_header_file(self, cr, uid, ids, writer, header_type,
                        definition_fields, context=None):
        "Only used in debug mode to display header in csv file"
        pass


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def check_country_code(self, cr, uid, ids, context=None):
        backend = self.get_logistic_backend(cr, uid, ids)
        order = self.browse(cr, uid, ids, context=context)[0]
        failed = False
        if backend and backend.version:
            if backend.version and backend.version[:9] == 'bleckmann':
                failed = True
                if order.partner_shipping_id:
                    sh = order.partner_shipping_id
                    if sh.country_id:
                        if pycountry.countries.get(alpha2=sh.country_id.code):
                            failed = False
        return failed


class RepositoryTask(orm.Model):
    _inherit = 'repository.task'

    def logistics_flow_trigger(self, cr, uid, flow, context=None):
        """ Crons calls this method """
        if not context:
            context = {}
        _, res_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'bleckmann_logistics', flow)
        if res_id:
            task = self.browse(cr, uid, res_id, context=context)
            context['logistic_id'] = task.repository_id.id
            _logger.info(' >>> logistics_flow_trigger: flow %s, task %s, '
                         'res %s', flow, task.name, res_id)
            return self.generate_file_document(cr, uid, task, context=context)


class Bleckmann(Logistic):
    FROM_SITE_ID = 'FROM_SITE_ID'  # Bleckmann info
    CLIENT_ID = 'CLIENT_ID'        # Bleckmann info
    LOGIS_DATE = 'YYYYMMDDHHMISS'

    _dialect = LogisticDialect()

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == BACKEND_VERSION

    def __init__(self, *args, **kwargs):
        "It fails if no __init__"

    def convert_date(self, string_date):
        " date format is YYYYMMDDHHMMSS"
        if string_date:
            return string_date.replace(
                ' ', '').replace('-', '').replace(':', '')
        return ''

    def get_allowed_values(self, allowed):
        """Allowed comes Bleckmann data"""
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

    def get_default_value(self, field):
        res = ''
        alloweds = self.get_allowed_values(field['Allowed Values'])
        # '\xc2\xa0' is non break char in bleckmann file
        default = field['Default'].strip("'").strip().replace('\xc2\xa0', '')
        if default in alloweds:
            res = default
            res = ''    # bleckmann requirements
        else:
            if '9' in alloweds[0]:
                res = '0'
                res = ''    # bleckmann requirements
            else:
                res = alloweds[0]
                res = ''    # bleckmann requirements
        return res

    def get_partner_infos(self, browse_model):
        vals = {}
        addr_fields = ['street', 'street2', 'zip', 'city']
        parent = browse_model.partner_id.parent_id
        partner = browse_model.partner_id
        vals['contact_name'] = partner.name
        vals['customer_id'] = parent.ref or partner.ref or ''
        vals['name'] = parent.name or partner.name or ''
        vals['email'] = partner.email or parent.email or ''
        vals['fax'] = partner.fax or parent.fax or ''
        vals['lang'] = partner.lang or parent.lang or ''
        vals['county'] = ((partner.state_id and partner.state_id.name) or
                          (parent.state_id and parent.state_id.name) or '')
        vals['phone'] = (partner.phone or partner.mobile or
                         parent.phone or parent.mobile or '')
        browse_partner = browse_model['partner_id']
        if partner.use_parent_address is True:
            browse_partner = browse_model['partner_id']['parent_id']
        for field in addr_fields:
            # TODO replace by safe_eval when when
            # I have figured out how it works
            browse_field_addr = eval('browse_partner.' + field)
            if browse_field_addr:
                value = sanitize(browse_field_addr)
            else:
                value = ''
            vals.update({field: value})
        vals['alpha3'] = pycountry.countries.get(
            alpha2=browse_partner.country_id.code).alpha3
        return vals

    def _get_values(self, main_values, definition_fields):
        """
        :param main_values: e.g.
            {'Action': 'A', 'Qty': '5'}
        :type main_values: :py:class:`Dict`
        :param definition_fields: e.g.
           [ {"Number": "2", "Name": "Action", "Type": "String", "Length": "1",
            "Required": "Required", "Allowed Values": "'A' | 'U' | 'D'",
            "Default": " ",}, {...}, ... ]
        :type definition_fields: List of Dict
        :rtype: list
        """
        values = []
        main_keys = main_values.keys()
        for field in definition_fields:
            if field.get('Name') in main_keys:
                # values are hard-coded in this case
                value = main_values[field['Name']]
                if not value:
                    value = ''
                values.append(value)
            else:
                # values are determined by definition_fields
                values.append(self.get_default_value(field))
        return values

    def prepare_incoming(self, picking, incoming_head):
        return {
            'Record Type': 'PAH',
            'Merge Action': 'A',
            'Pre Advice Id': str(picking.id),
            'Site Id': self.FROM_SITE_ID,
            'Owner Id': '01',
            'Name': sanitize(picking.partner_id.name),
            'Client Id': self.CLIENT_ID,
            'User Def Type 1': str(picking.id),
            'User Def Type 6': 'INCOMING',
            'User Def Num 1': '0.0',
            'Order Date': self.convert_date(picking.date),
        }

    def prepare_incoming_line(self, move, incoming_line):
        return {
            'Record Type': 'PAL',
            'Merge Action': 'A',
            'Pre Advice Id': str(move.picking_id.id),
            'Line Id': str(move.id),
            'Sku Id': '%s%s' % (str(move.product_id.default_code), SKU_SUFFIX),
            'Condition Id': 'NBO',
            'Qty Due': move.product_qty,
            'Client Id': self.CLIENT_ID,
            'User Def Date 1': self.convert_date(move.picking_id.date),
        }

    def prepare_picking(self, picking, delivery_head):
        part = self.get_partner_infos(picking)
        sale = picking.sale_id or ''
        return {
            'Record Type': 'ODH',
            'Merge Action': 'A',
            'Order Id': str(picking.id),
            'From Site Id': self.FROM_SITE_ID,
            'Customer Id': str(part['customer_id']),
            'Name': part['name'][:30],
            'Address1': part['street'],
            'Address2': part['street2'],
            'Town': part['city'],
            'Postcode': part['zip'],
            'County': part['county'],
            'Country': part['alpha3'],
            'Owner Id': '01',
            'Client Id': self.CLIENT_ID,
            'Status': 'Released',
            'Order Date': self.convert_date(picking.date),
            'Contact': part['contact_name'],
            'Contact Phone': part['phone'],
            'Contact Email': part['email'],
            'Instructions': sanitize(picking.note) or '',
            'Order Reference': sanitize(picking.origin) or '',
            'Purchase Order': sale and sale.client_order_ref or '',
            'Freight Terms': sale and sale.incoterm.code or '',
        }

    def prepare_move(self, move, delivery_line):
        return {
            'Record Type': 'ODL',
            'Merge Action': 'A',
            'Order Id': str(move.picking_id.id),
            'Line Id': str(move.id),
            'Sku Id': '%s%s' % (str(move.product_id.default_code), SKU_SUFFIX),
            'Qty Ordered': move.product_qty,
            'Client Id': self.CLIENT_ID,
            # 'User Def Type 5' is the brand : Inherit this method
            # in your own module to change this value
            'User Def Type 5': '',
            'Product Price': '0',
            'Product Currency': move.price_currency_id.name,
            'Notes': '',
            # you may inherit this method
            # in your own module to change these values
            'Customer Sku Id': '',
            'Customer Sku Desc1': '',
        }

    def prepare_catalog(self, product, sku):
        "These are required field"
        return {
            'Record Type': 'SKU',
            'Merge Action': 'A',
            # you may inherit this method
            # in your own module to change these values
            'Sku Id': '%s%s' % (str(product.default_code), SKU_SUFFIX),
            'Description': product.name,
            'User Def Note 1': sanitize(product.description),
            'Ean': product.ean13,
            'Each Weight': product.weight,
            'Each Volume': product.volume,
            'Product Group': self.CLIENT_ID,
            'Putaway Group': self.CLIENT_ID,
            'Client Id': self.CLIENT_ID,
            'Incub Rule': '',
            'Ce Vat Code': '',
            'Count Frequency': '0',
            'User Def Type 1': '',
            'User Def Type 7': '',
            'Family Group': '',
        }

    def _should_i_set_header(self, model_browse):
        res = (False, False)
        elm = model_browse
        logistic_id = elm._context.get('logistic_id')
        backend = elm._model.pool['logistic.backend'].browse(
            elm._cr, elm._uid, logistic_id, elm._context)
        if backend and hasattr(backend, 'column_in_file'):
            if backend.column_in_file:
                res = (True, backend)
        return res

    def _check_field_length(self, vals, flow, flow_name=None):
        "Check if data doesn't overcome the length of the field"
        exceptions = {}
        for field in flow:
            to_collect = False
            fname = field.get('Name')
            if vals.get(fname):
                if field.get('Type') in ('Integer'):
                    if len(str(vals[fname])) > int(field.get('Length')):
                        to_collect = True
                if field.get('Type') in ('String', 'Flag', 'Date'):
                    if len(vals[fname]) > int(field.get('Length')):
                        to_collect = True
                # if field.get('Type') in ('Decimal'):  # TODO
                if to_collect:
                    key = flow_name or '_'
                    exceptions.update({key: {fname: {
                        'data': vals[fname],
                        'max_length': field.get('Length')}}})
        return exceptions

    def check_logistics_data(self, browse):
        vals2write = {}
        if browse._name == 'product.product':
            vals2write['logistics_to_check'] = False
            vals = self.prepare_catalog(browse, sku)
            exceptions = self._check_field_length(vals, sku)
            if exceptions:
                self.notify_exceptions(browse, exceptions, values=vals2write)
            else:
                # logistics exception on product must be dropped
                if browse.logistics_exception:
                    vals2write['logistics_exception'] = False
        if vals2write:
            browse.write(vals2write)
        return True

    def export_catalog(self, products, writer, non_compliant_ids):
        product_data = []
        header, backend = self._should_i_set_header(products[0])
        for product in products:
            if header:
                backend.set_header_file(writer, 'MASTER', sku)
            vals = self.prepare_catalog(product, sku)
            product_data = self._get_values(vals, sku)
            writer.writerow(product_data)
        if product_data:
            _logger.info(" >>> 'export_catalog' fct ADD data")
            return True
        else:
            _logger.info(" >>> 'export_catalog' no data to export")
            return False

    def export_delivery_order(self, pickings, writer, non_compliant_ids):
        data_to_send = False
        header, backend = self._should_i_set_header(pickings[0])
        for picking in pickings:
            data = []
            exceptions = defaultdict(dict)
            if header:
                backend.set_header_file(writer, 'MASTER', delivery_head)
            vals = self.prepare_picking(picking, delivery_head)
            exceptions.update(self._check_field_length(
                    vals, delivery_head, 'head'))
            data.append(self._get_values(vals, delivery_head))
            for move in picking.move_lines:
                if header:
                    backend.set_header_file(writer, 'RELATED', delivery_line)
                # if move.state in ['assigned']:
                vals = self.prepare_move(move, delivery_line)
                exceptions.update(
                    self._check_field_length(vals, delivery_line, 'line'))
                data.append(self._get_values(vals, delivery_line))
            if exceptions:
                self.notify_exceptions(picking, exceptions,
                                       model='stock.picking')
                non_compliant_ids.append(picking.id)
            elif data:
                picking.write({'logistics_exception': False})
                data_to_send = True
                for elm in data:
                    writer.writerow(elm)
        if data_to_send:
            _logger.info(" >>> 'export_delivery_order' ADD picking data")
            return True
        else:
            _logger.info(" >>> 'export_delivery_order' no data to export")
            return False

    def export_incoming_shipment(self, pickings, writer, non_compliant_ids):
        move_data = []
        header, backend = self._should_i_set_header(pickings[0])
        for picking in pickings:
            if header:
                backend.set_header_file(writer, 'MASTER', incoming_head)
            vals = self.prepare_incoming(picking, incoming_head)
            incoming_data = self._get_values(vals, incoming_head)
            writer.writerow(incoming_data)
            for move in picking.move_lines:
                if header:
                    backend.set_header_file(writer, 'RELATED', incoming_line)
                if move.state in ['assigned']:
                    vals = self.prepare_incoming_line(move, incoming_line)
                    move_data = self._get_values(vals, incoming_line)
                    writer.writerow(move_data)
        if move_data:
            _logger.info(" >>> 'export_incoming_shipment' ADD incoming data")
            return True
        else:
            _logger.info(" >>> 'export_incoming_shipment' no data")
            return False

    def notify_exceptions(self, browse, exceptions, values=None, model=None):
        mess_vals = {
            'subject': u"Bleckmann exceptions: Too wide data",
            'body': u"Here is problematic keys <br/>\n%s"
                    % json.dumps(exceptions),
            'model': model or browse._name,
            'res_id': browse.id,
            'type': 'notification'}
        browse._model.pool['mail.message'].create(
            browse._cr, browse._uid, mess_vals, context=browse._context)
        if values:
            values['logistics_exception'] = True
