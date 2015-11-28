# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Pricelists extension",
    "version" : "1.0",
    "author" : "Elico Corp",
	"website" : "http://www.openerp.net.cn",
    "category" : "Sales",
    "depends" : ["base", "product"],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    This module adds a new form to be able to  directly filter and change pricelists rules.
    This is particularly useful for pricelists containing long lists of rules since the standard 
    pricelist form cannot filter rules  
    """,
    'update_xml': [
        'pricelist_extension_view.xml',
    ],
    'test':[],
    'installable': True,
    'active': False,
    'certificate': '',
}
