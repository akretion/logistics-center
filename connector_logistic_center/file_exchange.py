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

from openerp.osv import orm, fields
import logging
import base64
#from csv import Dialect
#from _csv import QUOTE_NONNUMERIC
from cStringIO import StringIO
import unicodecsv

_logger = logging.getLogger(__name__)

# TODO BUG active false in task view

LOGISTIC_TYPES = (
    ('logistic', 'Logistic'),
    ('logistic_inventory', 'Logistic inventory'),
    ('logistic_incoming', 'Logistic incoming'),
    ('logistic_delivery', 'Logistic delivery'),
)


class FileDocument(orm.Model):
    _inherit = "file.document"

    def get_file_document_type(self, cr, uid, context=None):
        res = super(FileDocument, self).get_file_document_type(
            cr, uid, context=context)
        res.extend(LOGISTIC_TYPES)
        return res

    def get_datas_from_file(self, cr, uid, file_doc, fields, dialect,
                            encoding="utf-8", context=None):
        str_io = StringIO()
        str_io.writelines(base64.b64decode(file_doc.datas))
        str_io.seek(0)
        return unicodecsv.DictReader(str_io, fieldnames=fields,
                                     encoding=encoding, dialect=dialect)

    def import_datas(self, cr, uid, file_doc, backend, context=None):
        """ Implement in your own module """

    def create(self, cr, uid, vals, context=None):
        if 'file_type' not in vals:
            vals.update({'file_type': 'logistic'})
        return super(FileDocument, self).create(cr, uid, vals, context=context)

    def _run(self, cr, uid, file_doc, context=None):
        super(FileDocument, self)._run(cr, uid, file_doc, context=context)
        if file_doc.file_type[:8] == 'logistic' \
                and file_doc.direction == 'input':
            if file_doc.repository_id:
                self.import_datas(cr, uid, file_doc,
                                  file_doc.repository_id.logistic_backend_id,
                                  context=context)


class FileRepository(orm.Model):
    _inherit = 'file.repository'

    _columns = {
        'logistic_backend_id': fields.many2one(
            'logistic.backend',
            'Logistic backend')
    }

    _sql_constraints = [
        ('logistic_backend_id_uniq', 'unique(logistic_backend_id)',
         "'Logistic backend' with the same ID already exists : must be unique"),
    ]


class RepositoryTask(orm.Model):
    _inherit = 'repository.task'
    #TODO : define tasks to display inactive tasks too

    def _get_method(self, cr, uid, context=None):
        return self.get_method(cr, uid, context=context)

    def get_method(self, cr, uid, context=None):
        """ Can be inherited to add custom values"""
        return [
            ('export_catalog', 'Export catalog'),
            ('export_incoming_shipment', 'Export incoming shipment'),
            ('export_delivery_order', 'Export delivery order'),
        ]

    _columns = {
        'model_id': fields.many2one(
            'ir.model',
            'Model',
            help="Model on which defined the method"),
        'method': fields.selection(
            _get_method,
            string='Method',
            size=100,
            help="Method called by the task"),
        'file_doc_id': fields.many2one(
            'file.document',
            'File doc',
            help="Link to the last created 'file document'"),
    }

    def open_file_document_button(self, cr, uid, ids, context=None):
        task = self.browse(cr, uid, ids, context=context)[0]
        return {
            'name': 'File Document',
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'file.document',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': unicode([('id', '=', task.file_doc_id.id)]),
        }

    def generate_file_document(self, cr, uid, task, context=None):
        kwargs = eval('self.pool[task.model_id.model].' + task.method)(
            cr, uid, [context['logistic_id']], task.last_exe_date,
            context=context)
        ids_from_model = []
        if isinstance(kwargs, dict):
            if 'ids_from_model' in kwargs:
                # records ids impacted by datas file export
                ids_from_model = kwargs.pop('ids_from_model')
            if 'file_datas' in kwargs and 'datas_fname' in kwargs:
                vals = self.update_doc_vals(
                    cr, uid, task, kwargs, context=context)
                vals = {'file_doc_id': self.create_file_document(
                    cr, uid, vals, ids_from_model, task, context=None)}
                self.write(cr, uid, [task.id], vals, context=context)
        return True

    def create_file_document(self, cr, uid, vals, ids_from_model, task,
                             context=None):
        """You may inherit this method to add behaviour
        after (or before) file doc creation
        e.g. you may fill in 'stock.picking' model the
        'log_out_file_doc_id' m2o field (from 'file.document')

        :param ids_from_model: list: record ids eventually used to
            apply orm write to have bindings between file content and erp ids
        :param task: browse repository.task: allow to
            define specific action according to task.method
        """
        return self.pool['file.document'].create(cr, uid, vals, context=context)

    def run(self, cr, uid, ids, context=None):
        """ Execute the repository task.
        Features are delegated to task.model, task.method
        """
        super(RepositoryTask, self).run(cr, uid, ids, context=context)
        for task in self.browse(cr, uid, ids, context=context):
            if not task.active:
                continue
            if task.direction == 'out':
                _logger.info('Start to run export task %s' % task.name)
                self.generate_file_document(cr, uid, task, context=context)
        return True

    def update_doc_vals(self, cr, uid, task, kwargs, context=None):
        vals = super(RepositoryTask, self).prepare_document_vals(
            cr, uid, task, kwargs['datas_fname'], kwargs['file_datas'],
            context=context)
        vals.update({
            'file_type': 'logistic',
            'active': kwargs.get('active', True),
            'sequence': kwargs.get('sequence', True),
            'direction': 'output',
        })
        return vals


class AutomaticTask(orm.Model):
    _inherit = 'automatic.task'

    # TODO debug import datas
    def get_task_type(self, cr, uid, context=None):
        types = super(AutomaticTask, self).get_task_type(cr, uid, context=context)
        types.extend(LOGISTIC_TYPES)
        return types
