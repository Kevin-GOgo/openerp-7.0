# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
