# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class historic_prices(orm.TransientModel):
    """ inherit this class to support duty zone cost prices.
    """
    _inherit = 'historic.prices'
   

    def action_open_window(self, cr, uid, ids, context=None):
        """
        Open the historical prices view

        rewrite this function to set the context to be able to dynamically
        select the cost to show in the list view.
        """
        res = super(historic_prices, self).action_open_window(
            cr, uid, ids, context=context)
        ctx = res.get('context').copy()
        wiz = self.browse(cr, uid, ids, context=context)[0]
        duty_zone = wiz.location_id.duty_zone_id
        if duty_zone:
            cost_type = duty_zone.price_type_id.field
        else:
            cost_type = 'standard_price'
        ctx.update(cost_type=cost_type)
        res.update(context=ctx)

        # use the inherited view
        d_obj = self.pool.get('ir.model.data')
        product_view_id = d_obj.get_object_reference(
            cr, uid,
            'stock_landed_costs',
            'LC_view_product_price_history')
        res.update(view_id=product_view_id[1])
        return res

