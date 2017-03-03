# -*- coding: utf-8 -*-
# © 2016 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Account Analytic Defaults',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Set default values for your analytic accounts.
==============================================

Allows to automatically select analytic accounts based on criterions:
---------------------------------------------------------------------
    * Product
    * Partner
    * User
    * Company
    * Date
    """,
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'images': ['images/analytic_defaults.jpeg'],
    'depends': ['account', 'sale_stock', 'sale','point_of_sale'],
    'data': [
        'security/ir.model.access.csv', 
        'security/account_analytic_default_security.xml', 
        'account_analytic_default_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}


