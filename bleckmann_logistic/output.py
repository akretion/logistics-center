# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author David BEAL <david.beal@akretion.com>
#     @author Sebastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import re
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.connector_logistic_center.logistic import (
    Logistic,)
from .common import LogisticDialect, BACKEND_VERSION
import logging
from .data.flow_delivery import delivery_head, delivery_line
from .data.flow_sku import sku
from .data.flow_incoming import incoming_head, incoming_line

_logger = logging.getLogger(__name__)

# Required logistic_center_dev if you want to use logistic debug mode
LOGISTIC_DEBUG = False
# see logistic_center_dev for more information
DEBUG_DISPLAY_COLUMN = False

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
    if isinstance(string, (str, unicode)):
        if '\n' in string:
            # \n can't be in string because there is QUOTING_NONE in csv dialect
            string.replace('\n', ' ')
        if ';' in string:
            # ; is the delimiter and must not be in string
            string.replace(';', ',')
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

    def get_datas_to_export(self, cr, uid, backend_ids, model, model_ids,
                            export_method, flow, backend_version, context=None):
        self.logistic_debug_mode(cr, uid, backend_ids, context=context)
        LOGISTIC_DEBUG = self.LOGISTIC_DEBUG
        if hasattr(self, 'DEBUG_DISPLAY_COLUMN'):
            DEBUG_DISPLAY_COLUMN = self.DEBUG_DISPLAY_COLUMN
        return super(LogisticBackend, self).get_datas_to_export(
            cr, uid, backend_ids, model, model_ids, export_method, flow,
            backend_version, context=context)

    def _prepare_doc_vals(self, cr, uid, backend_version, file_datas, model_ids,
                          flow, context=None):
        vals = super(LogisticBackend, self)._prepare_doc_vals(
            cr, uid, backend_version, file_datas, model_ids, flow, context=context)
        if DEBUG_DISPLAY_COLUMN:
            vals.update({'active': False})
        return vals

    def export_catalog(self, cr, uid, ids, last_exe_date, context=None):
        product_ids = self.get_product_ids(
            cr, uid, ids[0], last_exe_date, context=context)
        if product_ids:
            product_m = self.pool['product.product']
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
                ('log_out_file_doc_id', '=', False),
                ('logistic_center', '=', str(ids[0])),
            ],
            context=context)
        if picking_ids:
            kwargs = self.get_datas_to_export(
                cr, uid, ids, picking_m, picking_ids, 'export_delivery_order',
                FLOWS['export_delivery_order'], BACKEND_VERSION, context=context)
            return kwargs
        return True

    def export_incoming_shipment(self, cr, uid, ids, last_exe_date,
                                 context=None):
        incoming_sh_m = self.pool['stock.picking']
        incoming_sh_ids = incoming_sh_m.search(
            cr, uid, [
                ('state', 'in', ('assigned',)),
                ('type', '=', 'in'),
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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def check_country_code(self, cr, uid, ids, context=None):
        backend = self.get_logistic_backend(cr, uid, ids)
        order = self.browse(cr, uid, ids, context=context)[0]
        failed = False
        if backend and backend.version:
            if backend.version and backend.version[:8] == 'bleckmann':
                if order.partner_shipping_id:
                    sh = order.partner_shipping_id
                    if sh.country_id and sh.country_id.alpha3:
                        failed = False
                    else:
                        failed = True
                else:
                    failed = True
        return failed


class RepositoryTask(orm.Model):
    _inherit = 'repository.task'

    def create_file_document(self, cr, uid, file_doc_vals, ids_from_model,
                             task, context=None):
        file_doc_id = super(RepositoryTask, self).create_file_document(
            cr, uid, file_doc_vals, ids_from_model, task, context=None)
        if not DEBUG_DISPLAY_COLUMN and task.method in \
                ['export_delivery_shipment', 'export_incoming_shipment']:
            vals = {'log_out_file_doc_id': file_doc_id}
            self.pool['stock.picking'].write(
                cr, uid, ids_from_model, vals, context=context)
        return file_doc_id


class Bleckmann(Logistic):
    INCLUDED_HEADER_MASTER = False
    INCLUDED_HEADER_RELATED = False
    FROM_SITE_ID = 'FROM_SITE_ID'  # Bleckmann info
    CLIENT_ID = 'CLIENT_ID'        # Bleckmann info
    LOGIS_DATE = 'YYYYMMDDHHMISS'

    _dialect = LogisticDialect()

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == BACKEND_VERSION

    def __init__(self, *args, **kwargs):
        "It fails if no __init__"

    def set_header_file(self, writer, header_type, definition_fields):
        "Only used in debug mode to display header in csv file"
        if DEBUG_DISPLAY_COLUMN:
            for htype in ('MASTER', 'RELATED'):
                if header_type == htype and \
                        eval('self.INCLUDED_HEADER_' + htype) is False:
                    num = range(1, len(definition_fields))
                    writer.writerow([])
                    writer.writerow(num)
                    require = []
                    for elm in definition_fields:
                        if elm['Required'] == 'Required':
                            require.append(self.DEBUG_FIELD_REQUIRED_MARK)
                        else:
                            require.append('')
                    writer.writerow(require)
                    header = [elm['Name'] for elm in definition_fields]
                    writer.writerow(header)
                    if htype == 'MASTER':
                        self.INCLUDED_HEADER_MASTER = True
                    else:
                        self.INCLUDED_HEADER_RELATED = True
        return True

    def convert_date(self, string_date):
        " date format is YYYYMMDDHHMMSS"
        if string_date:
            return string_date.replace(' ', '').replace('-', '').replace(':', '')
        else: return ''

    def get_allowed_values(self, allowed):
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
        #'\xc2\xa0' is non break char in bleckmann file
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

    def get_partner_infos(self, browse_model, addr_complement=None):
        vals = {}
        addr_fields = ['street', 'street2', 'zip', 'city']
        if addr_complement:
            addr_fields.extend(addr_complement)
        parent = browse_model.partner_id.parent_id
        partner = browse_model.partner_id
        vals['contact_name'] = partner.name
        vals['name'] = parent.name or partner.name or ''
        vals['email'] = partner.email or parent.email or ''
        vals['fax'] = partner.fax or parent.fax or ''
        vals['lang'] = partner.lang or parent.lang or ''
        vals['phone'] = partner.phone or partner.mobile or parent.phone \
            or parent.mobile or ''
        browse_partner = browse_model['partner_id']
        if partner.use_parent_address is True:
            browse_partner = browse_model['partner_id']['parent_id']
        for field in addr_fields:
            #TODO replace by safe_eval when I would understood how it works
            browse_field_addr = eval('browse_partner.' + field)
            if browse_field_addr:
                value = sanitize(browse_field_addr)
            else:
                value = ''
            vals.update({field: value})
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
            'Sku Id': str(move.product_id.id) + '.zz',
            'Condition Id': 'NBO',
            'Qty Due': move.product_qty,
            'Client Id': self.CLIENT_ID,
            'User Def Date 1': self.convert_date(move.picking_id.date),
        }

    def prepare_picking(self, picking, delivery_head):
        part = self.get_partner_infos(picking, ['country_id.alpha3'])
        return {
            'Record Type': 'ODH',
            'Merge Action': 'A',
            'Order Id': str(picking.id),
            'From Site Id': self.FROM_SITE_ID,
            'Customer Id': str(picking.partner_id.id),  # TODO parent
            'Name': part['name'],
            'Address1': part['street'],
            'Address2': part['street2'],
            'Town': part['city'],
            'Postcode': part['zip'],
            'Country': part['country_id.alpha3'],
            'Owner Id': '01',
            'Client Id': self.CLIENT_ID,
            'Status': 'Released',
            'Order Date': self.convert_date(picking.date),
            'Contact': part['contact_name'],
            'Contact Phone': part['phone'],
            'Contact Email': part['email'],
            'Instructions': sanitize(picking.note) or '',
            'Order Reference': sanitize(picking.origin) or '',
        }

    def prepare_move(self, move, delivery_line):
        return {
            'Record Type': 'ODL',
            'Merge Action': 'A',
            'Order Id': str(move.picking_id.id),
            'Line Id': str(move.id),
            'Sku Id': str(move.product_id.id) + '.zz',
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
            'Sku Id': str(product.id) + '.zz',
            'Description': sanitize(product.default_code),
            'User Def Note 1': sanitize(product.name),
            'User Def Note 2': sanitize(product.description),
            'Ean': product.ean13,
            'Each Weight': product.weight,
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

    def export_catalog(self, products, writer):
        product_data = []
        for product in products:
            self.set_header_file(writer, 'MASTER', sku)
            vals = self.prepare_catalog(product, sku)
            product_data = self._get_values(vals, sku)
            writer.writerow(product_data)
        if product_data:
            return True
        else:
            return False

    def export_delivery_order(self, pickings, writer):
        move_data = []
        for picking in pickings:
            self.set_header_file(writer, 'MASTER', delivery_head)
            vals = self.prepare_picking(picking, delivery_head)
            picking_data = self._get_values(vals, delivery_head)
            writer.writerow(picking_data)
            for move in picking.move_lines:
                self.set_header_file(writer, 'RELATED', delivery_line)
                if move.state in ['assigned']:
                    vals = self.prepare_move(move, delivery_line)
                    move_data = self._get_values(vals, delivery_line)
                    writer.writerow(move_data)
        if move_data:
            return True
        else:
            return False

    def export_incoming_shipment(self, pickings, writer):
        move_data = []
        for picking in pickings:
            self.set_header_file(writer, 'MASTER', incoming_head)
            vals = self.prepare_incoming(picking, incoming_head)
            incoming_data = self._get_values(vals, incoming_head)
            writer.writerow(incoming_data)
            for move in picking.move_lines:
                self.set_header_file(writer, 'RELATED', incoming_line)
                if move.state in ['assigned']:
                    vals = self.prepare_incoming_line(move, incoming_line)
                    move_data = self._get_values(vals, incoming_line)
                    writer.writerow(move_data)
        if move_data:
            return True
        else:
            return False
