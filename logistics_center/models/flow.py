# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models, fields
from .logistics import get_logistics_parser

_logger = logging.getLogger(__name__)


class LogisticsFlow(models.Model):
    _name = 'logistics.flow'
    _description = 'Logistics flows attached to logistics backend'

    name = fields.Char(required=True)
    logistics_backend_id = fields.Many2one(
        string='Backend logistics', required=True,
        comodel_name='logistics.backend',
        ondelete='cascade',
        help="Logistics Backend where flow is attached")
    flow = fields.Selection(
        selection=[
            ('delivery', 'Delivery'), ('incoming', 'Incoming'),
            ('catalog', 'Catalog')],
        required='True',
        help="Typical logistics flow to implement with an "
             "external logistics center")
    direction = fields.Selection(
        selection=[('export', 'Export'), ('import', 'Import')],
        string='Direction', required='True',
        help="Way followed by the flow")
    impacted_record = fields.Integer(
        string='Todo', compute='_compute_impacted_records')
    last_message = fields.Text(string="Last message", readonly=True)
    last_doc_id = fields.Many2one(
        comodel_name='ir.attachment', readonly=True, string="Last file")
    last_date = fields.Datetime(string='Last date')

    def _get_logistics(self):
        return get_logistics_parser(self.logistics_backend_id.code)

    def run(self):
        self.ensure_one()
        logistics = self._get_logistics()
        kwargs = logistics.run_flow(self)
        attachment = self._save_attachment(kwargs)
        do = [x.name for x in kwargs['records']]
        body = ("Bons de livraison associés à la dernière "
                "demande de livraison: %s\n\n%s" % (self.name, do))
        self.write({
            'last_doc_id': attachment.id,
            'last_date': False,
            'last_message': "BL %s" % do,
        })
        kwargs['records'].write({
            'log_out_file_doc_id': attachment.id,
        })
        self.logistics_backend_id.message_post(body=body)

    @api.model
    def _save_attachment(self, kwargs):
        # {'records': stock.picking(1,),
        #  'file_datas': b'RTtTVEYvT1Vi4wCg==',
        #  'sequence': 70, 'name': '1.1 delivery_order 2019-02-21_15-49-10',
        #  'datas_fname': 'del_order_2019-02-21_15-49-10.csv', 'active': True}
        attachment = self.env['ir.attachment'].create({
            'external_type': self.logistics_backend_id.code,
            'datas': kwargs['file_datas'],
            'sending_date': self.last_date,
            'name': kwargs['datas_fname'],
            'datas_fname': kwargs['datas_fname']})
        return attachment

    def button_see_impacted_records(self):
        self.ensure_one()
        logistics = self._get_logistics()
        return {
            "name": _("Impacted flow: %s" % self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': logistics._get_domain(self),
            'target': 'current',
        }

    def _get_records_to_process(self):
        logistics = self._get_logistics()
        domain = logistics._get_domain(self)
        records = self.env['stock.picking'].search(domain)
        _logger.info("Flow '%s' retrieve '%s' records with domain %s " % (
            self.name, len(records), domain))
        return records

    def _compute_impacted_records(self):
        for rec in self:
            logistics = rec._get_logistics()
            domain = logistics._get_domain(rec)
            rec.impacted_record = self.env['stock.picking'].search_count(
                domain)
            _logger.debug("Flow '%s' retrieve '%s' records with domain %s " % (
                rec.name, rec.impacted_record, domain))
