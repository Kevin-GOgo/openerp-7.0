# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class pos_order_line(orm.Model):
    _inherit = 'pos.order.line'

    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        return super(pos_order_line, self)._amount_line_all(
            cr, uid, ids, field_names, arg, context=context)

    _columns = {
        'price_subtotal': fields.function(
            _amount_line_all,
            multi='pos_order_line_amount',
            string='Subtotal w/o Tax'),
        'price_subtotal_incl': fields.function(
            _amount_line_all,
            multi='pos_order_line_amount',
            string='Subtotal'),
    }
