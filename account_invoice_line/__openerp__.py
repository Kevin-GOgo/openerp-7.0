# -*- coding: utf-8 -*-
# © 2016 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Invoice Line',
    'version': '1.1',
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
    'images' : [],
    'depends': ['account'],
    'data': [
        'account_view.xml',        
        'security/ir.model.access.csv',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: