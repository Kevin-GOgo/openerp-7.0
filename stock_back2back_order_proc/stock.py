# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from osv import fields, orm
from tools.translate import _
import netsvc
import tools

class stock_location(orm.Model):
    _inherit = "stock.location"
    
    def picking_type_get(self, cr, uid, from_location, to_location, context=None):
        """ Gets type of picking.
        @param from_location: Source location
        @param to_location: Destination location
        @return: Location type
        """
        result = 'internal'
        if (from_location.usage=='internal') and (to_location and to_location.usage in ('customer', 'supplier')):
            result = 'out'
        elif (from_location.usage in ('supplier', 'customer')) and (to_location.usage in ('internal', 'supplier')): # Also consider inter-supplier picking as IN. Ian@Elico 
            result = 'in'
        return result
    
    _columns = {
        'retention_mode': fields.selection(
            [('retention', 'Retention Mode'), ('thru', 'Thru mode')],
            'Retention Mode',
            required=True,
            help="In 'Retention mode' the system wait for the whole quantity before the stuff is processed.\n" \
                "In 'Thru mode' the shipped quantity is processed regardless of the ordered quantity."
            ),
    }
    _defaults = {
        'retention_mode': 'retention',
    }

stock_location()



class stock_picking(orm.Model):
    _inherit = "stock.picking"
    

    def get_move_chain(self, cr, uid, move_id, context=None, move_obj=False):
        '''Recursively get the chained moves
        @return list of the chained moves
        '''
        if not move_obj:
            move_obj = self.pool.get('stock.move')
        move_tbc = move_obj.browse(cr, uid, move_id, context, move_obj)
        
        if move_tbc.move_dest_id: # If there is move_dest_id in the chain
            move_chain = self.get_move_chain(cr, uid, move_tbc.move_dest_id.id, context)
        else:
            move_chain = []       
        
        move_chain.append(move_tbc)
        
        return move_chain
    
    
    def copy_pick_chain(self, cr, uid, all_moves, context=None):
        '''Copy all the picking related to this order
        @return the dictionary of couple: old_pick_id => new_pick_id
        '''
        new_picks = {}
        all_chained_moves = []
        sequence_obj = self.pool.get('ir.sequence')
        
        for move in all_moves:
            all_chained_moves.extend(self.get_move_chain(cr, uid, move.id, context))
            
        for move in all_chained_moves:
            if move.picking_id.id and not new_picks.has_key(move.picking_id.id):                
                pick_tbc = self.browse(cr, uid, move.picking_id.id, context)
                new_note = ((pick_tbc.note if pick_tbc.note else '') + ' Copy of stock.pick[%d].') % move.picking_id.id 
                new_pick_id = self.copy(cr, uid, move.picking_id.id, {
                                                           'state': 'draft',
                                                           'note': new_note,
                                                           'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick_tbc.type)),
                                                           'move_lines' : [],
                })
                
                new_picks[move.picking_id.id] = new_pick_id
        
        return new_picks
    

    def copy_move_chain(self, cr, uid, move_id, product_qty, new_picks, context=None, move_obj=False):
        '''Recursively copy the chained move until a location in retention mode or the end.
        @return id of the new first move.
        '''
        if not move_obj:
            move_obj = self.pool.get('stock.move')
        move_tbc = move_obj.browse(cr, uid, move_id, context)
        move_dest_id = False
        
        if move_tbc.move_dest_id and move_tbc.location_dest_id.retention_mode == 'thru': # If there is move_dest_id in the chain and the current location is in thru mode, we need to make a copy of that, then use it as new move_dest_id.
            move_dest_id = self.copy_move_chain(cr, uid, move_tbc.move_dest_id.id, product_qty, new_picks, context, move_obj)
        
        my_picking_id = (new_picks[move_tbc.picking_id.id] if new_picks.has_key(move_tbc.picking_id.id) else False)
        
        new_note = ((move_tbc.note if move_tbc.note else '') + ' Copy of stock.move[%d].') % move_id 
        new_move_id = move_obj.copy(cr, uid, move_id, {
                                                   'move_dest_id': move_dest_id,
                                                   'state': 'waiting',
                                                   'note': new_note,
                                                   'move_history_ids': False, # Don't inherit child, populate it in next step. The same to next line.
                                                   'move_history_ids2': False,
                                                   'product_qty' : product_qty,
                                                   'product_uos_qty': product_qty,
                                                   'picking_id' : my_picking_id,
                                                   'price_unit': move_tbc.price_unit,
                                                    })        
        
        
        if move_dest_id: # Create the move_history_ids (child) if there is.
            move_obj.write(cr, uid, [new_move_id], {'move_history_ids': [(4, move_dest_id)]})
        return new_move_id
    
    
    def update_move_chain_pick(self, cr, uid, move_id, vals, new_picks, context=None):
        '''Recursively update the new chained move with the new related picking by the first move id until a location in retention mode or the end.
        @return True if ok.
        '''
        move_obj = self.pool.get('stock.move')
        move_tbu = move_obj.browse(cr, uid, move_id, context)
        
        while True:            
            vals.update(picking_id=new_picks[move_tbu.picking_id.id])
            move_obj.write(cr, uid, [move_tbu.id], vals, context)
            
            if not move_tbu.move_dest_id or move_tbu.location_dest_id.retention_mode != 'thru':
                break
            
            move_tbu = move_tbu.move_dest_id            
        return True
    
    
    def update_move_chain(self, cr, uid, move_id, vals, context=None):
        '''Recursively update the old chained move by the first move id until a location in retention mode or the end.
        @return True if ok.
        '''
        ids = [move_id]
        move_obj = self.pool.get('stock.move')
        move_tbu = move_obj.browse(cr, uid, move_id, context)
        
        while move_tbu.move_dest_id and move_tbu.location_dest_id.retention_mode == 'thru':
            ids.append(move_tbu.move_dest_id.id)
            move_tbu = move_tbu.move_dest_id
            
        move_obj.write(cr, uid, ids, vals, context)
        return True
            

    def isPickNotEmpty(self, cr, uid, pick_id, move_obj, context=None):
        cpt = move_obj.search(cr, uid,
                          [ ('picking_id', '=', pick_id),],
                          context=context, count=True)        
        return cpt > 0
    
    
    def check_production_node_move_chain(self, cr, uid, move_tbc, context=None):
        if move_tbc.location_id.usage == 'production':
            return True        
        
        if move_tbc.move_dest_id:
            if self.check_production_node_move_chain(cr, uid, move_tbc.move_dest_id, context):
                return True
        return False
        
        
    def hasProductionNode(self, cr, uid, all_moves, context=None):       
        for move in all_moves:
            if self.check_production_node_move_chain(cr, uid, move, context):
                return True
        return False


    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picks = False
            complete, too_many, too_few, all_moves = [], [], [], []
            move_product_qty = {}
            prodlot_ids = {}
            product_avail = {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                #Commented in order to process the less number of stock moves from partial picking wizard
                #assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
                product_qty = partial_data.get('product_qty') or 0.0
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom') or False
                product_price = partial_data.get('product_price') or 0.0
                product_currency = partial_data.get('product_currency') or False
                prodlot_id = partial_data.get('prodlot_id') or False
                prodlot_ids[move.id] = prodlot_id
                
                all_moves.append(move)
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})

            if not too_few:
                res = super(stock_picking, self).do_partial(cr, uid, [pick.id], partial_datas, context=context)
                
            else:
                if self.hasProductionNode(cr, uid, all_moves, context=context):# check if there is a production location in the chain 
                    res[pick.id] = super(stock_picking, self).do_partial(cr, uid, [pick.id], partial_datas, context=context)
                    #res[pick.id]['warning'] = {'title': _('Warning'), 'message': _('One of your location destinations type is Production. Only the first pick has been split.')}
                
                else:
                    new_picks = self.copy_pick_chain(cr, uid, all_moves, context)
                
                    for move in too_few:
                        product_qty = move_product_qty[move.id] #actual received quantity
                        
                        if product_qty != 0:
                            """Copy not only one move, but all the moves where the destination location is in THRU MODE """                
                            new_move_id = self.copy_move_chain(cr, uid, move.id, product_qty, new_picks, context)
                            
                            prodlot_id = prodlot_ids[move.id]
                            if prodlot_id:
                                self.update_move_chain(cr, uid, new_move_id, {
                                    'prodlot_id' : prodlot_id,
                                }, context)                    
                            
                            """Update the old moves with the remaining quantity"""
                            self.update_move_chain(cr, uid, move.id, {
                                'product_qty' : move.product_qty - product_qty,
                                'product_uos_qty':move.product_qty - product_qty,#TODO: put correct uos_qty
                            }, context)
            
                        else:
#EC                            self.write(cr, uid, [move.id],
                            move_obj.write(cr, uid, [move.id],#EC
                                    {
                                        'states' : 'waiting',
                                    })            
                        
                    for move in complete:
                        defaults = {}
                        if prodlot_ids.get(move.id):
                            defaults.update(prodlot_id=prodlot_id)
        
                        if move.location_id.retention_mode == 'thru':
                            self.update_move_chain_pick(cr, uid, move.id, defaults, new_picks, context)
                        else:
                            move_obj.write(cr, uid, [move.id], {'picking_id' : new_picks[move.picking_id.id]}, context)
                    
                    
                    for move in too_many:
                        product_qty = move_product_qty[move.id]
                        defaults = {}
                        defaults_1st_move = {
                            'picking_id' : new_picks[move.picking_id.id],
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                        }
                        prodlot_id = prodlot_ids.get(move.id)
                        if prodlot_ids.get(move.id):
                            defaults.update(prodlot_id=prodlot_id)
                            defaults_1st_move.update(prodlot_id=prodlot_id)
        
                        move_obj.write(cr, uid, [move.id], defaults_1st_move, context)
                        if move.location_id.retention_mode == 'thru':
                            self.update_move_chain_pick(cr, uid, move.id, defaults, new_picks, context)
                        else:
                            move_obj.write(cr, uid, [move.id], {'picking_id' : new_picks[move.picking_id.id]}, context)                    
        
        
                    # At first we confirm the new pickings (if necessary)              
                    for old_pick, new_pick in new_picks.iteritems():
                        
                        # check if the old pick is empty
                        if not self.isPickNotEmpty(cr, uid, old_pick, move_obj, context):
                            self.unlink(cr, uid, [old_pick])
                                            
                            
                        # check if the new pick is not empty
                        if self.isPickNotEmpty(cr, uid, new_pick, move_obj, context):
                            if self.isPickNotEmpty(cr, uid, old_pick, move_obj, context):
                                self.write(cr, uid, [old_pick], {'backorder_id': new_pick})
                                wf_service.trg_validate(uid, 'stock.picking', new_pick, 'button_confirm', cr)
                                self.action_move(cr, uid, [new_pick])
                        else:
                            self.unlink(cr, uid, [new_pick])
                    
                    #pick.refresh()  <= Works on 6.1
                    # Here we set the moves as "assigned"
                    pick_hack = self.browse(cr, uid, pick.id, context=context)
                    for move in pick_hack.backorder_id.move_lines:
                        move_obj.action_assign(cr, uid, [move.id])
                    
                    # The pick is set as "confirmed" then "done"
                    wf_service.trg_validate(uid, 'stock.picking', new_picks[pick.id], 'button_done', cr)
                    wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                    
                    #pick.refresh()  <= Works on 6.1
                    # Finally we set the next pick as "assigned"
                    pick_hack = self.browse(cr, uid, pick.id, context=context)
                    for move in pick_hack.backorder_id.move_lines:
                        if move.move_dest_id.picking_id and self.test_assigned(cr, uid, [move.move_dest_id.picking_id.id]):
                            self.action_assign_wkf(cr, uid, [move.move_dest_id.picking_id.id], context=context)
                    
                    res[pick.id] = {'delivered_picking': new_picks[pick.id] or False}

        return res
    
stock_picking()







class stock_move(orm.Model):
    _name = "stock.move"
    _inherit = "stock.move"
    
    
    def copy_move_chain(self, cr, uid, move_id, product_qty, context=None):
        '''Recursively copy the chained move until a location in retention mode or the end.
        @return id of the new first move.
        '''
        move_tbc = self.browse(cr, uid, move_id, context)
        move_dest_id = False
        
        if move_tbc.move_dest_id and move_tbc.location_dest_id.retention_mode == 'thru': # If there is move_dest_id in the chain and the current location is in thru mode, we need to make a copy of that, then use it as new move_dest_id.
            move_dest_id = self.copy_move_chain(cr, uid, move_tbc.move_dest_id.id, product_qty, context)        
        
        new_note = ((move_tbc.note if move_tbc.note else '') + ' Copy of stock.move[%d].') % move_id 
        new_move_id = self.copy(cr, uid, move_id, {
                                                   'move_dest_id': move_dest_id,
                                                   'state': 'waiting',
                                                   'note': new_note,
                                                   'move_history_ids': False, # Don't inherit child, populate it in next step. The same to next line.
                                                   'move_history_ids2': False,
                                                   'product_qty' : product_qty,
                                                   'product_uos_qty': product_qty,
                                                   'picking_id' : move_tbc.picking_id.id,
                                                   'price_unit': move_tbc.price_unit,
                                                    })
        
        
        
        if move_dest_id: # Create the move_history_ids (child) if there is.
            self.write(cr, uid, [new_move_id], {'move_history_ids': [(4, move_dest_id)]})
        return new_move_id
    
    
    def update_move_chain(self, cr, uid, move_id, vals, context=None):
        '''Recursively update the chained move by the first move id until a location in retention mode or the end.
        @return True if ok.
        '''
        ids = [move_id]
        move_tbu = self.browse(cr, uid, move_id, context)        
        move_location = self.browse(cr, uid, move_tbu.location_id, context)
        
        while move_tbu.move_dest_id and move_tbu.location_dest_id.retention_mode == 'thru':
            ids.append(move_tbu.move_dest_id.id)
            move_tbu = move_tbu.move_dest_id
        self.write(cr, uid, ids, vals, context)
        return True
    
            
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """       
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s'%(move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
            product_qty = partial_data.get('product_qty',0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom',False)
            product_price = partial_data.get('product_price',0.0)
            product_currency = partial_data.get('product_currency',False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                            move_currency_id, product_price)
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                            product.uom_id.id)
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context)[product.id]
                        new_std_price = ((amount_unit * product.qty_available)\
                            + (new_price * qty))/(product.qty_available + qty)

                    product_obj.write(cr, uid, [product.id],{'standard_price': new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency,
                                })

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                
                """Copy not only one move, but all the moves where the destination location is in THRU MODE """
                new_moves = self.copy_move_chain(cr, uid, move.id, product_qty, context)
                #Andy: new_moves is one id, not an id list, 2012-09-28, so 
                #for new_move in new_moves:
                    #complete.append(self.browse(cr, uid, new_move))
                complete.append(self.browse(cr, uid, new_move))
                #End by Andy

                """Update not only one move, but all the moves where the destination location is in THRU MODE """
                self.update_move_chain(cr, uid, [move.id], {
                            'product_qty' : move.product_qty - product_qty,
                            'product_uos_qty':move.product_qty - product_qty,
                        }, context)

            else:
                self.write(cr, uid, [move.id],
                        {
                            'states' : 'waiting',
                        })
                


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],{'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]
