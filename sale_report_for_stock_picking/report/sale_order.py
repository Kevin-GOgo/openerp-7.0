# -*- coding: utf-8 -*-
# © 2016 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


import time

from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
TC_OnTrade="""
DELIVERY POLICY | 运输政策
Delivery times: order before 4pm for next day delivery. Same day and weekend delivery possible under special request.
发货时间：工作日下午4点前下单者，次日发货。亦可根据客户特殊需求于下单当日或周末发货。
Delivery free of charge in Shanghai, Chengdu and Beijing. Other destinations, delivery fee of 100RMB, delivery free of charge for orders of 1000RMB and above.
上海、成都、北京三个城市免运费。其它目的地，运费为100元人民币。订单金额达1000元人民币或以上者，免运费。
"""
TC_Private="""
DELIVERY POLICY | 运输政策
Delivery times: order before 4pm for next day delivery. Same day and weekend delivery possible under special request.
发货时间：工作日下午4点前下单者，次日发货。亦可根据客户特殊需求于下单当日或周末发货。
Delivery free of charge in Shanghai, Chengdu and Beijing. Other destinations, delivery fee depends on customer and destination, delivery free of charge for orders of 1500RMB and above.
上海、成都、北京三个城市免运费。其它目的地，快递费用取决于顾客及目的地。订单金额达1500元人民币或以上者，免运费。
"""
class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        # Warning on internal picking if there is not sale order
        if context is None:
            context = {}
        picking_obj = pooler.get_pool(cr.dbname).get('stock.picking')
        if context.get('active_ids',False):
            for picking in picking_obj.browse(cr, uid, context['active_ids'], context=context):
                if not picking.sale_id:
                    raise osv.except_osv(_('Warning!'), _('There is no related sale order to this delivery document. Please use picking slip instead.'))        
        super(order, self).__init__(cr, uid, name, context=context)


        self.localcontext.update({
            'time': time,
            'show_discount': self._show_discount,
            'terms_conditions':self._terms_conditions,
            'get_total_qty':self._get_total_qty,
        })
    #TODO 是否考虑将内容增加到记录中，供用户修改。
    def _terms_conditions(self,):
         if self.name =='sale.order.private':
             return TC_Private
         elif self.name =='sale.order.without.discount':
             return TC_OnTrade
         else:
             return ''
    def _get_total_qty(self, so):
        qty = sum([x.product_uom_qty for x in so.order_line])
        return qty
        
    def _show_discount(self, uid, context=None):
        cr = self.cr
        try:
            group_id = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(
            cr, uid, uid, context=context).groups_id]

report_sxw.report_sxw(
    'report.sale.order.picking.without.discount', 'stock.picking',
    'addons/sale_report_for_stock_picking/report/sale_order_without_discount.rml',
    parser=order, header="external")

