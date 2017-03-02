# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
{'name': 'Multi Company Salesperson',
 'version': '7.0.1.0.0',
 'depends': ['sale'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
1. Customer can be shared among different companies.
2. Salesman is required for every customer.
3. One salesperson(user) might belong to different companies
and might switch to another company.
 """,
 'data': [
         'security/multi_company_orders.xml',
         'security/ir.model.access.csv',
         'partner_view.xml'],
 'installable': True,
 'application': False}
