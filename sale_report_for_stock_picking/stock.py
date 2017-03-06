# -*- coding: utf-8 -*-
# © 2016 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
    }
    _defaults = {
    }

    def print_sale_report(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order of stock picking
        '''
        assert len(ids) == 1, 'This option should only be used for\
         a single id at a time'
        sale_pool = self.pool.get('sale.order')

        picking = self.read(cr, uid, ids[0], ['origin'], context=context)
        sale_ids = sale_pool.search(cr, uid,
                                    [('name', '=', picking['origin'])],
                                    context=context)
        if len(sale_ids) != 1:
            raise osv.except_osv(_('No Sale Report'),
                                 _("There should be one sale order\
                                  linked to this picking."))
        # check by line before
        datas = {'model': 'sale.order',
                 'ids': sale_ids,
                 'form': sale_pool.read(cr, uid, sale_ids[0], context=context),
                 }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'sale.order.without.discount',
                'datas': datas, 'nodestroy': True}

