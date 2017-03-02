# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm


class pos_session(orm.Model):
    _inherit = 'pos.session'

    def wkf_check_final_balance(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            for st in record.statement_ids:
                if st.journal_id.type == 'bank':
                    st.write(
                        {'balance_end_real': st.balance_end})
