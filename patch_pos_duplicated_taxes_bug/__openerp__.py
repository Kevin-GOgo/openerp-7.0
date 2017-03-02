# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

{'name': 'Patch POS duplicated taxes bug',
 'version': '7.0.1.0.0',
 'category': 'Generic Modules',
 'depends': ['point_of_sale'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
 This module solves the bug: unbalanced journal items from pos orders.
 Because the calculation of taxes is messed up with multi companies.
""",
 'installable': True,
 'application': False,
 }
