# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{'name': 'Patch update ending balance',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['point_of_sale'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 For details, please check issue:2432
 Stable-Total transactions and ending balance are different in a POS session.
""",
 'data': ['pos_workflow.xml'],
 'installable': True,
 'application': False,
 }
 