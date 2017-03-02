# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{'name': 'Purchase Landed Costs -- Duty zones',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['account', 'stock',
             'purchase_landed_costs_extended',
             'anglo_saxon_account_pos', 'account_anglo_saxon',
             'sale_automatic_workflow'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Modification on purchase_landed_costs:
    * no invoices created for landed cost any more when the po confirmed.

Limitations:
    *
""",
 'data': [
     'security/landed_cost_security.xml',
     'security/ir.model.access.csv',
     'wizard/historic_prices_view.xml',
     'wizard/stock_change_standard_price_view.xml',
     'wizard/generate_invoice_from_picking_view.xml',
     'stock_view.xml',
     'product_view.xml'],
 'installable': True,
 'application': False,
 }
