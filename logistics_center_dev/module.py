# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID

CRON_TO_INACTIVE = {
    'ir_cron_enqueue_jobs': 'connector',
}


class IrCron(orm.Model):
    _inherit = 'ir.cron'

    _columns = {
        'logistic_center_dev': fields.integer(
            'Intial active state',
            help="Cron active field value before logistic_center_dev installation"
            "(0: untouched cron, 1: False, 2: True)",
        )
    }


class Module(orm.Model):
    _inherit = 'ir.module.module'

    def init(self, cr):
        uid = SUPERUSER_ID
        cron_m = self.pool['ir.cron']
        for cron in CRON_TO_INACTIVE:
            model, res_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, CRON_TO_INACTIVE[cron], cron)
            if cron_m.browse(cr, uid, res_id).active is True:
                state = 2
            else:
                state = 1
            vals = {'logistic_center_dev': state,
                    'active': False}
            cron_m.write(cr, uid, [res_id], vals)

    def button_immediate_uninstall(self, cr, uid, ids, context=None):
        cron_m = self.pool['ir.cron']
        context.update({'active_test': False})
        cron_ids = cron_m.search(
            cr, uid, [('logistic_center_dev', 'in', (1, 2))], context=context)
        for cron in cron_m.browse(cr, uid, cron_ids, context=context):
            active = False
            if cron.logistic_center_dev == 2:
                active = True
            cron.write({'active': active})
        return super(Module, self).button_immediate_uninstall(cr, uid, ids,
                                                              context=context)
