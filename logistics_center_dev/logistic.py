# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields

DEBUG_FIELD_REQUIRED_MARK = '!! Required !!'


class LogisticBackend(orm.Model):
    _inherit = 'logistic.backend'
    INCLUDED_HEADER_MASTER = False
    INCLUDED_HEADER_RELATED = False

    _columns = {
        'logistic_debug': fields.boolean(
            'Logistics Debug',
            help="Allow to generate 'File document' in debug mode"
                 "(see module description for more help)"),
        'column_in_file': fields.boolean(
            'Column name ',
            help="Allow to display column names in csv files if implemented "
                 "by your logistics module (file.document must be created "
                 "with active filed to False)"),
    }

    _defaults = {
        'logistic_debug': True,
        'column_in_file': False,
    }

    def _prepare_doc_vals(
            self, cr, uid, backend_version, file_datas, model_ids,
            flow, context=None):
        vals = super(LogisticBackend, self)._prepare_doc_vals(
            cr, uid, backend_version, file_datas, model_ids, flow,
            context=context)
        logistics_id = context.get('logistic_id')
        if logistics_id:
            backend = self.browse(cr, uid, logistics_id, context=context)
            if backend.column_in_file:
                vals.update({'active': False})
        return vals

    def set_header_file(self, cr, uid, ids, writer, header_type,
                        definition_fields, context=None):
        "Only used in debug mode to display header in csv file"
        for htype in ('MASTER', 'RELATED'):
            if (header_type == htype and
                    eval('self.INCLUDED_HEADER_' + htype) is False):
                num = range(1, len(definition_fields))
                writer.writerow([])
                writer.writerow(num)
                require = []
                for elm in definition_fields:
                    if elm['Required'] == 'Required':
                        require.append(DEBUG_FIELD_REQUIRED_MARK)
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


class RepositoryTask(orm.Model):
    _inherit = 'repository.task'

    def create_file_document(self, cr, uid, file_doc_vals, ids_from_model,
                             task, context=None):
        file_doc_id = super(RepositoryTask, self).create_file_document(
            cr, uid, file_doc_vals, ids_from_model, task, context=None)
        if (not task.repository_id.logistic_backend_id.column_in_file and
                task.method in ['export_delivery_order',
                                'export_incoming_shipment']):
            vals = {'log_out_file_doc_id': file_doc_id}
            self.pool['stock.picking'].write(
                cr, uid, ids_from_model, vals, context=context)
        return file_doc_id
