# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class res_partner(orm.Model):
        _inherit = 'res.partner'

        _columns = {
            # add a new field to allow the partner to be shared
            # among different companies.
            'company_ids': fields.many2many(
                'res.company',
                'res_company_partner_rel',
                'partner_id', 'cid', 'Allowed Companies',
                groups='base.group_multi_company'),
        }

        def _default_company_ids(self, cr, uid, context=None):
            user_obj = self.pool.get('res.user')
            user_ids = user_obj.search(
                cr, uid, [('id', '=', uid)], context=context)
            return user_ids

        _defaults = {
            'company_ids': _default_company_ids
        }
