# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Sales Order improvement',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Base',
    'description': """
Extension to module sale to improve the order of the UoM in the sales
order lines form.  """,
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'depends': ['sale'],
    'update_xml': ['sale_order_improvement_view.xml'],
    'installable': True,
    'active': False,
}
