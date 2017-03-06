# -*- coding: utf-8 -*-
# © 2016 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Sale Report for Stock Picking',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': 'Print Sale Report in interface of stock picking',
    'description': """
         Print Sale Report (On Trader) for Stock Picking
    """,
    'depends': ['sarment_sale_report', 'stock'],
    'category': 'Warehouse Management',
    'sequence': 10,
    'data': [
        'stock_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}

