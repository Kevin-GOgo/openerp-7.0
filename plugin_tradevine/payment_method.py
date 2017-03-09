# -*- coding: utf-8 -*-
# -*-coding:utf-8-*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields


class payment_method(orm.Model):
    _inherit = 'payment.method'

    _columns = {
        'code': fields.char('Code'),
    }
