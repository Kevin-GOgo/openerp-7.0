# -*- coding: utf-8 -*-
# © 2014 Elico corp(www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class ProductUl(osv.osv):
    _inherit = 'product.ul'

    def _get_cbm(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        for ul in self.browse(cr, uid, ids, context=context):
            cbm = ul.high * ul.width * ul.long
            cbm = cbm != 0 and cbm / 1000000
            res[ul.id] = cbm
        return res

    _columns = {
        'name': fields.char('name', size=32),
        'high': fields.float(
            'H (cm)', digits_compute=dp.get_precision('Pack Height')),
        'width': fields.float(
            'W (cm)', digits_compute=dp.get_precision('Pack Height')),
        'long': fields.float(
            'L (cm)', digits_compute=dp.get_precision('Pack Height')),
        'cbm': fields.function(
            _get_cbm, arg=None, type='float',
            string='CBM',
            digits_compute=dp.get_precision('Pack Height')),
    }

