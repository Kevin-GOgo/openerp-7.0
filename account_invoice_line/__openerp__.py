# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Account Invoice Line',
    'version': '7.0.1.0.0',
    'category': 'Account',
    'sequence': 19,
    'summary': 'Invoice line',
    'description': """
Invoice Line
==================================================
Fine tune Account Invoice Line
    """,
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'depends': ['account'],
    'data': [
        'account_view.xml',        
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

