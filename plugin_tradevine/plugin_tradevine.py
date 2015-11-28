# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
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

from openerp.osv import osv, fields
import urllib2
import time
from hashlib import sha1
from random import random
import requests
from collections import Iterable
import json
import logging
_logger = logging.getLogger(__name__)
MAX_SEQUENCE_NUM = 5000

Base_Url = u'https://api.tradevine.com'
Request_Token_Url = u'https://api.tradevine.com/v1/RequestToken'
Access_Token_Url = u'https://api.tradevine.com/v1/AccessToken'
Authorise_Url_Token = u'https://nz.tradevine.com/API/v1/Authorise'
API_Authority = u'https://api.tradevine.com'
Consumer_Key = u'40a99dbb-4fee-4fb3-8f68-72760d7471de'
Consumer_Secret = u'c58c3086-38dc-45e8-ad9f-092cca71818a'
Access_Token_Key = u'd6ed94aa-78d0-4744-a58f-1227a053afe9'
Access_Token_Secret = u'b67dd513-d5ed-4a18-9a38-ca4560d29ab7'
Consumer_Key1 = u'50fddadb­9d7e­4d13­84da­4f9aa8483cc4'
Consumer_Secret1 = u'c39cd0c9­7aa5­4c92­a948­53ed00571848'
Access_Token_Key1 = u'95a4f5c8­6e47­4ce7­80d4­c1ad260e546d'
Access_Token_Secret1 = u'3ccb1e80­adae­4040­8de4­2c1353e261b2'
oauth_token = u'd6ed94aa-78d0-4744-a58f-1227a053afe9'
oauth_consumer_key = u'40a99dbb-4fee-4fb3-8f68-72760d7471de'
oauth_signature = u'c58c3086-38dc-45e8-ad9f-092cca71818a%2526b67dd513-d5ed-4a18-9a38-ca4560d29ab7'


class tradevine_setting(osv.osv):
    """ Tradevine API Setting """
    _name = "tradevine.setting"
    _description = "Tradevine API Setting"

    def _get_product_value(self, prod, field):
        if hasattr(prod, field):
            return getattr(prod, field)
        else:
            return ""

    def _prepare_product_values(self, cr, uid, prod, context=None):
        #TODO sync product's QoH.
        values = {
            "OrganisationID": "",
            "Code": self._get_product_value(prod, 'default_code'),
            "Name": prod.name or '',
            "Description": "",
            "AlternateCode": self._get_product_value(prod, 'default_code'),
            "UnitOfMeasure": prod and prod.uom_id and prod.uom_id.name or '',
            "Barcode": self._get_product_value(prod, 'ean13'),
            "InternalNotes": "",
            "ExternalNotes": "",
            "ProductCategoryID": prod and prod.categ_id and prod.categ_id.name
            or '',
            # "Weight": self._get_product_value(prod, 'weight'),
            # "Length": self._get_product_value(prod, 'length'),
            # "Width": self._get_product_value(prod, 'width'),
            # "Height": self._get_product_value(prod, 'height'),
            "Currency": "",
            "TaxClassID": "",
            "TaxCode": self._get_tax_code(prod),
            "WarehouseStock": "",
            "QuantityAvailableToSell": "",
            "QuantityAvailableToShip": "",
            "CostPrice": self._get_product_value(prod, 'standard_price'),
            "SellPriceIncTax": "",
            "SellPriceExTax": "",
            "MinimumStockQuantity": "",
            "OverrideSalesGLAccountCode": "",
            "OverrideSalesGLAccountName": "",
            "OverridePurchaseGLAccountCode": "",
            "OverridePurchaseGLAccountName": "",
            "PhotoIdentifier": "",
            "IsManualOrderApprovalNeeded": "",
            "CreatedDate": "",
            "CreatedBy": "",
            "ModifiedDate": "",
            "ModifiedBy": ""
        }
        return values

    def _get_tax_code(self, prod):
        taxes = ''
        if prod and prod.taxes_id:
            for tax in prod.taxes_id:
                taxes += tax.description + ' '
        return taxes

    def _prepare_auth_parameter(self, cr, uid, context=None):
        nonce_val = sha1(str(random())).hexdigest()
        ts = time.time()
        params = {
            'oauth_token': 'd6ed94aa-78d0-4744-a58f-1227a053afe9',
            'oauth_nonce': nonce_val,
            'oauth_consumer_key': '40a99dbb-4fee-4fb3-8f68-72760d7471de',
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_timestamp': str(round(ts)).rstrip('0').rstrip('.'),
            'oauth_version': '1.0',
            'oauth_signature': 'c58c3086-38dc-45e8-ad9f-092cca71818a%2526b67dd513-d5ed-4a18-9a38-ca4560d29ab7'
        }
        return params

    # def show_all_product_from_tradevine(self, cr, uid, context=None):
    #     url = 'https://api.tradevine.com/v1/Product'
    #     context = context or {}
    #     tradevineUrl = self.generate_url(cr, uid, 1, context)
    #     content = self.access_tradevine_api(cr, uid, tradevineUrl, context)
    #     result = json.load(content)
    #     total_count = result["TotalCount"]
    #     page_size = result["PageSize"]
    #     page_number = result["PageNumber"]
    #     print "TotalCount: ", total_count, "PageSize : ", page_size

    def sync_tradevine_product_id(self, default_code):
        if not default_code:
            return 0, None
        #see if tradevine already has this porduct.
        url = 'https://api.tradevine.com/v1/Product/'
        nonce_val = sha1(str(random())).hexdigest()
        ts = time.time()
        url1 = url + '?code='
        url1 = url1 + str(default_code)
        url1 = url1 + '&oauth_token=95a4f5c8-6e47-4ce7-80d4-c1ad260e546d&oauth_nonce='
        url1 = url1 + nonce_val
        url1 = url1 + '&oauth_consumer_key=50fddadb-9d7e-4d13-84da-4f9aa8483cc4&oauth_signature_method=PLAINTEXT&oauth_timestamp='
        url1 = url1 + str(round(ts)).rstrip('0').rstrip('.')
        url1 = url1 + '&oauth_version=1.0&oauth_signature=c39cd0c9-7aa5-4c92-a948-53ed00571848%25263ccb1e80-adae-4040-8de4-2c1353e261b2'
        content = urllib2.urlopen(url1)
        result = json.load(content)
        if result:
            return result['TotalCount'], result['List']
        return 0, None

    def create_products_into_tradevine(self, cr, uid, context=None):
        '''
            sync all products on OpenERP that are not on tradevine.
            this is the main function execute in cron job.
        '''
        context = context or {}
        #url should not specify ProductID
        url = 'https://api.tradevine.com/v1/Product/'
        headers = {'content-type': 'application/json'}
        obj_prod = self.pool.get('product.product')

        #only sync product that can be sold.
        prod_ids = obj_prod.search(
            cr, uid,
            [('tradevine_product_id', '=', False), ('sale_ok', '=', True)])
        for prod in obj_prod.browse(cr, uid, prod_ids, context):
            values = self._prepare_product_values(
                cr, uid, prod, context)
            params = self._prepare_auth_parameter(cr, uid, context)
            #check if tradevine already has this product code.
            count, result = self.sync_tradevine_product_id(prod.default_code)
            if count:
                tradevine_product_id = result[0].get('ProductID', '')
                #write back the tradevineID to OpenERP
                obj_prod.write(
                    cr, uid, [prod.id],
                    {'tradevine_product_id': str(tradevine_product_id)},
                    context)
                if count > 1:
                    _logger.debug(
                        '***There are %d products share the same SKU!,'
                        'product SKU:%s\n' % (
                            count, prod.default_code))
                continue
            #if it comes to create a new product,
            #we should not specify the ProductID.
            response = requests.post(
                url, params=params,
                data=json.dumps(values),
                headers=headers, verify=False)

            if response.status_code == 200:
                    result = response.json()
                    if result["ProductID"]:
                        _logger.debug(
                            '***create product to TV,'
                            ' product SKU:%s, id:%s \n' % (
                                result['code'], result['ProductID']))
                        #write back the tradevineID to OpenERP
                        obj_prod.write(
                            cr, uid, [prod.id],
                            {'tradevine_product_id': str(result["ProductID"])},
                            context)
            else:
                _logger.error(
                    '***create product to TV,'
                    ' response state:%s \n, response Error: %s' % (
                        response.status_code, response.content))
            #TODO remove this after finishing test. only sync one product.
            #break
        return True


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'tradevine_customer_id': fields.char('Tradevine Customer ID', size=64),
        'tradevine_org_id': fields.char('Tradevine Organization Id', size=64),
        'tradevine_address_id': fields.char('Tradevine Address ID', size=64),
        'customer_code': fields.char('Customer Code', size=64),
        'terms_of_trade': fields.selection(
            [('4000', 'Immediate'),
             ('4001', 'Cash'),
             ('4002', '7 days'),
             ('4003', '20th of month following invoice'),
             ('4004', '14 days'),
             ('4005', '21 days'),
             ('4006', '28 days'),
             ('4007', '30 days'),
             ('4008', '60 days'),
             ('4009', '90 days')],
            'Terms of Trade'),
        'traffic_light': fields.selection(
            [('13001', 'Red'),
             ('13002', 'Orange'),
             ('13003', 'Green'),
             ('13004', 'Grey')],
            'Traffic Light'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(res_partner, self).name_get(
            cr, uid, ids, context=context)or []
        new_res = []
        for res_id, name in res:
            addr_type = self.read(
                cr, uid, [res_id], ['type'], context=context)
            addr_type = addr_type and addr_type[0].get('type') or ''
            if addr_type in ('invoice', 'delivery'):
                new_res.append((res_id, name + '(' + addr_type + ')'))
            else:
                new_res.append((res_id, name))
        return new_res


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'tradevine_line_id': fields.char('Tradevine Line ID', size=64),
        'tradevine_product_id': fields.char('Tradevine Product ID', size=64),
        'tax_rate': fields.float('Tax Rate'),
        'tax_total': fields.float('Tax Total'),
    }


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def getPaymentType(self, cr, uid, origin, context):
        obj_payment_method = self.pool.get('payment.method')
        pm_ids = obj_payment_method.search(cr, uid, [('code', '=', origin)])
        if pm_ids:
            return pm_ids[0]
        return False

    def getOrderOrigin(self, cr, uid, origin, context):
        if(origin == 3000):
            return "Manual"
        elif(origin == 3003):
            return "Trade Me"
        elif(origin == 3004):
            return "Shopify"
        return ""

    def getOrderState(self, cr, uid, origin, context):
        if origin == 12001:
            return "progress"
        elif origin == 12002:
            return "manual"
        elif origin == 12003:
            return "done"
        elif origin == 12004:
            return "cancel"
        return "draft"

    def getProduct(
            self, cr, uid, ProductID, code,
            context=None):
        context = context or {}
        product_obj = self.pool.get('product.product')
        ids = product_obj.search(
            cr, uid, [('default_code', '=', code)],
            context=context)
        if len(ids) > 1:
            _logger.debug(
                '***There are %d product %s in OpenERP'
                ' with the same tradevine_ids, and SKU:%s' % (
                    len(ids), ids, code))
        if ids:
            #write back the tradevine_product_id
            product_obj.write(
                cr, uid, ids, {'tradevine_product_id': ProductID})
            return product_obj.browse(cr, uid, ids, context=context)[0]
        else:
            return False

    def isnew_customer(self, cr, uid, CustomerID, context):
        '''check if the customer with the tradevine id exists
        '''
        if not CustomerID:
            return 0
        context = context or {}
        partner_obj = self.pool.get('res.partner')
        ids = partner_obj.search(
            cr, uid,
            [('tradevine_customer_id', '=', CustomerID),
             ('type', 'in', ('default', 'other', 'contact'))], context=context)
        return ids and ids[0] or 0

    def isnew_address(self, cr, uid, address, address_type, context=None):
        #check the street and city to see if the address exits in OE.
        #same street, city, tradevine_customer_id
        #if only zip is not right, then consider it the same address.
        #consider the addr is NULL.2014-04-21.('' == False) --> Fasle.
        if address:
            vals = self._convert_address_to_oe(cr, uid, address)
            partner_obj = self.pool.get('res.partner')
            domain = [('tradevine_customer_id', '=', address['CustomerID'])]
            if vals['street']:
                domain.append(('street', '=', vals['street']))
            if vals['city']:
                domain.append(('city', '=', vals['city']))

            partner_ids = partner_obj.search(cr, uid, domain)
            return partner_ids and partner_ids[0] or None
        else:
            #TODO if address is None you should raise an error.
            _logger.error("this address is None")

    def isnew_order(self, cr, uid, tv_so_id, context):
        context = context or {}
        order_obj = self.pool.get('sale.order')
        ids = order_obj.search(
            cr, uid, [('tradevine_so_id', '=', tv_so_id)], context=context)
        return ids and ids[0] or 0

    def isnew_line(self, cr, uid, line_id, context=None):
        context = context or {}
        line_obj = self.pool.get('sale.order.line')
        ids = line_obj.search(
            cr, uid, [('tradevine_line_id', '=', line_id)], context=context)
        return ids and ids[0] or 0

    def access_tradevine_api(self, cr, uid, url, context=None):
        content = urllib2.urlopen(url)
        return content

    #TODO rewrite this function to be more normal, extract the oauth etc.
    #sync sale order only 12001!!
    def generate_url(self, cr, uid, page_number, context=None):
        nonce_val = sha1(str(random())).hexdigest()
        ts = time.time()
        tradevineUrl = 'https://api.tradevine.com/v1/SalesOrder?pageNumber='
        tradevineUrl = tradevineUrl + str(page_number)
        tradevineUrl = tradevineUrl + '&status=12001'
        tradevineUrl = tradevineUrl + '&oauth_token=95a4f5c8-6e47-4ce7-80d4-c1ad260e546d&oauth_nonce='
        tradevineUrl = tradevineUrl + nonce_val
        tradevineUrl = tradevineUrl + '&oauth_consumer_key=50fddadb-9d7e-4d13-84da-4f9aa8483cc4&oauth_signature_method=PLAINTEXT&oauth_timestamp='
        tradevineUrl = tradevineUrl + str(round(ts)).rstrip('0').rstrip('.')
        tradevineUrl = tradevineUrl + '&oauth_version=1.0&oauth_signature=c39cd0c9-7aa5-4c92-a948-53ed00571848%25263ccb1e80-adae-4040-8de4-2c1353e261b2'
        return tradevineUrl

    def _get_partner_company_id(
            self, cr, uid, tradevine_org_id=None, context=None):
        '''get the organisation (company in OpenERP) id.
             if tradevine_org_id is None, return False
                    * if not exists, return False
                    * else, return the id.
        '''
        if tradevine_org_id is None:
            return False
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(
            cr, uid,
            [('tradevine_org_id', '=', tradevine_org_id),
             ('is_company', '=', True)])
        return partner_ids and partner_ids[0] or False

    def _get_customer_address_id(
            self, cr, uid, tradevine_customer_id,
            tradevine_address_id, tradevine_org_id=None,
            address_type='default', context=None):
        '''Get the customer address with specific type.
            different partners in openerp may share
            the same tradevine_customer_id and tradevine_org_id
            tradevine_org_id maybe None
        params:
                    *address_type: type in OpenERP,
                                [delivery]: Shipping
                                [invoice]: Invoice
                                [contact]: Contact
                                [default]: Default: use as both ??
        return:
                    * return the partner id if exists
                    * return False if not
        '''
        partner_obj = self.get('res.partner')
        #TODO if the conditions are too much.
        ids = partner_obj.search(
            cr, uid,
            [('tradevine_customer_id', '=', tradevine_customer_id)
             ('tradevine_org_id', '=', tradevine_org_id),
             ('tradevine_address_id', '=', tradevine_address_id),
             ('type', 'in', (address_type, ))])
        partner_id = ids and ids[0] or None
        partner_record = partner_obj.browse(cr, uid, partner_id)
        #in OpenERP, it may use parent address
        if partner_record and partner_record.use_parent_address\
                and partner_record.parent_id:
            return partner_record.parent_id.id or False
        return ids and ids[0] or False

    def _convert_address_to_oe(self, cr, uid, tradevine_address):
        #TODO country convert
        '''convert the address from tradevine to OpenERP
            *opener only has two streets.
            *return dict.
            * tradevine_address example:
                {u'ModifiedBy': 1,
                u'SupplierID': None,
                u'AddressID': 3511081115665275970,
                u'RegionState': None,
                u'Country': 8157,
                u'CreatedDate':
                u'2013-08-02T22:58:35.667Z',
                u'AddressLine2': u'',
                u'AddressLine3': u'newfield',
                u'CreatedBy': 1,
                u'AddressLine1': u'57 totara street',
                u'PostalCode': u'9812',
                u'TownCity': u'invercargill',
                u'DeliveryNotes': None,
                u'OrganisationID': 3466170600680106934,
                u'CustomerID': 3511034835295713456,
                u'ModifiedDate': u'2013-08-02T22:58:35.667Z'}
        '''
        val = {}
        if not tradevine_address:
            return val
        val['tradevine_address_id'] = tradevine_address['AddressID']
        val['street'] = tradevine_address['AddressLine1']
        val['city'] = tradevine_address['TownCity']
        val['zip'] = tradevine_address['PostalCode']
        # if people do it manually, you can write it over.
        # val['country_id'] = None
        return val

    def _get_customer_values(
            self, cr, uid, order, address_type='contact', context=None):
        '''get the vals used to create new partner, maybe a address
            params:
                * order: content from tradevine API. content['List'] line
                * address_type: type in OpenERP, default is 'default'
                                [delivery]: Shipping
                                [invoice]: Invoice
                                [contact]: Contact
                                [default]: Default: use as both
        '''
        customer_name = str(
            order['Customer']['FirstName']) + " " + str(
            order['Customer']['LastName'])
        if "None" in customer_name:
            #TODO raise except or sth, customer should have a name.
            customer_name = customer_name.replace("None", "")
            customer_name = customer_name.strip()

        vals = {
            'type': address_type,
            'parent_id': self._get_partner_company_id(
                cr, uid, order['OrganisationID']) or None,
            'tradevine_customer_id': order['Customer']['CustomerID'],
            'tradevine_org_id': order['Customer']['OrganisationID'],
            'customer_code': order['Customer']['CustomerCode'],
            'terms_of_trade': str(order['Customer']['DefaultTermsOfTrade']),
            'vat': order['Customer']['TaxNumber'],
            'traffic_light': order['Customer']['TrafficLight'] and str(
                order['Customer']['TrafficLight']) or None,
            'comment': order['Customer']['Notes'],
            'email': order['Customer']['Email'],
            'mobile': order['Customer']['MobileNumber'],
            'phone': order['Customer']['PhoneNumber'],
            'active': True,
            'customer': True,
            'name': customer_name,
            # 'notification_email_send': '',
        }
        if address_type == 'delivery':
            vals.update(self._convert_address_to_oe(
                cr, uid, order['ShippingAddress']))
        elif address_type == 'invoice':
            vals.update(self._convert_address_to_oe(
                cr, uid, order['BillingAddress']))
        else:
            #default is use the shipping address on tradevine.
            vals.update(self._convert_address_to_oe(
                cr, uid, order['ShippingAddress']))
        return vals

    def create_customer(self, cr, uid, order, context=None):
        """create new customer or address[shipping, invoice] if not exist.
                * update the latest address on TV to OE.

        Parameters
        ----------
        [order]: json content,
            contains order information and customer information in tradevine.
        Returns
        -------
        [return]: Customer_id
        """
        partner_obj = self.pool.get('res.partner')
        #same CustomerID and address type in contact, default, other
        customer_id = self.isnew_customer(
            cr, uid, order['CustomerID'], context)
        customer_vals = self._get_customer_values(
            cr, uid, order, address_type='contact')
        if customer_id == 0:
            customer_id = partner_obj.create(
                cr, uid, customer_vals, context=context)
        else:
            #check the latest information on tradevine
            #and write the newest information to OE.
            partner_obj.write(cr, uid, [customer_id], customer_vals)
        return customer_id

    def _get_default_pricelist(self, cr, uid, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        pricelist_ids = pricelist_obj.search(
            cr, uid, [('active', '=', True), ('type', '=', 'sale')])
        if not pricelist_ids:
            _logger.error(
                '***Error occurs when getting default pricelist!\n'
                'cannot get the pricelist!\n')
        return pricelist_ids[0]

    def get_so_values(self, cr, uid, order, customer_id, context=None):
        """get so values from the returned json content.

        Parameters
        ----------
        customer_id: OpenERP's partner_id
        order: json content return from tradevine api.
        https://api.tradevine.com/Help/api-reference/get-sales-orders.html

        Returns
        -------
        so_values to be used to create new SO.
        """
        #try:
        partner_obj = self.pool.get('res.partner')
        user = self.pool.get('res.users').browse(
            cr, uid, [uid], context=context)[0]
        company_id = user.company_id.id
        currency_id = user.company_id.currency_id.id
        payment_method = self.getPaymentType(
            cr, uid, str(order['PaymentType']), context)

        #LY patch do not create BillingAddress, ShippingAddress
        order['BillingAddress'] = None
        order['ShippingAddress'] = None
        #get partner_invoice_id
        if order['BillingAddress']:
            partner_invoice_id = self.isnew_address(
                cr, uid, order['BillingAddress'], address_type='invoice')
            vals = self._get_customer_values(
                cr, uid, order, address_type='invoice')
            if not partner_invoice_id:
                partner_invoice_id = partner_obj.create(cr, uid, vals)
        else:
            partner_invoice_id = customer_id

        #get partner_shipping_id
        if order['ShippingAddress']:
            partner_shipping_id = self.isnew_address(
                cr, uid, order['ShippingAddress'], address_type='delivery')
            vals = self._get_customer_values(
                cr, uid, order, address_type='delivery')
            if not partner_shipping_id:
                partner_shipping_id = partner_obj.create(cr, uid, vals)
        else:
            partner_shipping_id = customer_id

        so_vals = {
            #TODO shop_id. debfault pricelist is a bug.
            # 'shop_id': shop_id,
            # 'warehouse_id': warehouse_id,
            # 'payment_term': default_payment_term,
            # 'fiscal_position': default_fiscal_position,
            # 'order_policy': order_policy,
            'pricelist_id': self._get_default_pricelist(
                cr, uid, context=context) or False,
            'company_id': company_id,
            'currency_id': currency_id,
            'date_order': order['CreatedDate'],
            'invoice_quantity': 'order',
            'partner_invoice_id': partner_invoice_id or customer_id,
            'partner_shipping_id': partner_shipping_id or customer_id,
            'tradevine_so_id': order['SalesOrderID'],
            'tradevine_org_id': order['OrganisationID'],
            'partner_id': customer_id,
            'tv_order_number': order['OrderNumber'],
            'origin': self.getOrderOrigin(
                cr, uid, order['OrderOrigin'], context),
            'client_order_ref': (order['CustomerOrderReference'] or '') +
            (':' + order['OrderNumber'] or ''), #LY fix for None + ''
            'state': 'draft',
            'terms_of_trade': str(order['TermsOfTrade']),
            'payment_due_date': order['PaymentDueDate'],
            'is_payment_received': order['IsPaymentReceived'],
            'payment_date': order['PaymentDate'],
            'payment_method_id': payment_method,
            'shipping_type': str(order['ShipmentType']),
            'req_shipping_date': order['RequestedShippingDate'],
            'amount_untaxed': order['TotalCost'],
            'amount_tax': order['SubTotalApplicableTaxes'],
            'margin': order['GrossProfit'],
            'amount_total': order['GrandTotal'],
            'note': order['InternalNotes'],
            'external_notes': order['ExternalNotes'],
            'completed_date': order['CompletedDate'],
            'billing_address': partner_invoice_id,
            'shipping_address': partner_shipping_id,
        }
        return so_vals

    def sale_order_hook(self, cr, uid, so_id, customer_id, context=None):
        '''this function executes after sale order is wrote or created.'''
        #trigger payment_method onchange.
        new_vals = self.read(cr, uid, so_id, ['payment_method_id'], context)
        payment_method_id = new_vals.get('payment_method_id', False)
        new_vals = payment_method_id and {
            'payment_method_id': payment_method_id[0]} or {}
        if new_vals:
            #trigger the onchange_partner_id
            new_vals.update(
                self.onchange_partner_id(
                    cr, uid, [], customer_id, context=context).get('value'))
            #trigger the payment_method onchange.
            if new_vals['payment_method_id'] and hasattr(
                    self, 'onchange_payment_method_id'):
                new_vals.update(self.onchange_payment_method_id(
                    cr, uid, so_id,
                    new_vals['payment_method_id'], context).get('value'))
            #trigger the onchange_process_id
            if 'workflow_process_id' in new_vals and hasattr(
                    self, 'onchange_workflow_process_id'):
                onchange_workflow_res = self.onchange_workflow_process_id(
                    cr, uid, [], new_vals['workflow_process_id'], context)
                new_vals.update(
                    onchange_workflow_res.get('value'))
            self.write(cr, uid, so_id, new_vals, context)
        return new_vals

    def create_sales_order(self, cr, uid, order, customer_id, context=None):
        so_vals = self.get_so_values(cr, uid, order, customer_id, context)
        so_obj = self.pool.get('sale.order')
        so_id = so_obj.create(cr, uid, so_vals, context=context)
        self.sale_order_hook(cr, uid, so_id, customer_id, context=context)
        print "Create Sales Order : ", order['SalesOrderID']
        return so_id

    def write_sales_order(
            self, cr, uid, order, so_id, customer_id, context=None):
        #LY update order only in draft
        so_vals = self.read(cr, uid, so_id, ['state'], context)
        so_state = so_vals.get('state', None)
        if so_state != 'draft':
            return so_id
        vals = self.get_so_values(cr, uid, order, customer_id, context)
        self.write(cr, uid, [so_id], vals)
        self.sale_order_hook(cr, uid, so_id, customer_id, context=context)
        return so_id

    def create_sales_line(self, cr, uid, order, so_id, context=None):
        try:
            user = self.pool.get('res.users').browse(
                cr, uid, [uid], context=context)[0]
            company_id = user.company_id.id
            if so_id > 0:
                for line in order['SalesOrderLines']:
                    line_id = self.isnew_line(
                        cr, uid, line['SalesOrderLineID'], context)
                    if line_id == 0:
                        product = self.getProduct(
                            cr, uid, line['ProductID'],
                            line['Code'], context)
                        if not product:
                            _logger.error(
                                'There is no such product in OpenERP now.\n'
                                "Product's SKU is %s and SO id is: %d" % (line['Code'], so_id))
                            return False
                        tax_ids = product.taxes_id
                        tax = []
                        for tax_id in tax_ids:
                            tax.append(tax_id.id)
                        line_Vals = {
                            'company_id': company_id,
                            'order_id': so_id,
                            'name': product.name_template,
                            'tradevine_line_id': line['SalesOrderLineID'],
                            'tradevine_product_id': line['ProductID'],
                            'product_id': product.id,
                            'product_uom_qty': line['Quantity'],
                            'purchase_price': line['CostPrice'],
                            'price_unit': line['SellPriceIncTax'],
                            'tax_rate': line['TaxRate'],
                            'tax_total': line['TaxTotal'],
                            'tax_id': [(6, 0, tax)]
                        }
                    #service product should be at last of the sale order lines.
                        if product.type == 'service':
                            line_Vals.update({'sequence': MAX_SEQUENCE_NUM})
                        line_id = self.pool.get('sale.order.line').create(
                            cr, uid, line_Vals, context=context)
                        print "Create Sales Line : ", line['SalesOrderLineID']
        except Exception, e:
            _logger.error(
                'Error occurs when creating sale order line!\n'
                'Error: %s' % str(e))

    def create_write_order(self, cr, uid, order, context=None):
        # create  sale order, payment is created
        # write sale order
        #
        context = context or {}
        try:
            if order['SalesOrderLines']:
                so_id = self.isnew_order(
                    cr, uid, order['SalesOrderID'], context=context)
                #check existing customer or not
                #also upate the latest address information.
                customer_id = self.create_customer(cr, uid, order, context)
                if so_id == 0:
                    if (customer_id > 0):
                        so_id = self.create_sales_order(
                            cr, uid, order, customer_id, context)
                        #LY Create prepayment after creation
                        #It's ugly, and 26003 is "PayNow","Cash","EFTPOS/Credit Card"
                        #when the code of tradevine changed
                        #please change the method automatic_payment--Alex
                        if order.get('PaymentType') in (
                                26003, 26001, 26008):
                            self.automatic_payment_tradevine(
                                cr, uid, [so_id], amount=None, context=context)
                else:
                    if (customer_id > 0):
                        so_id = self.write_sales_order(
                            cr, uid, order, so_id, customer_id, context)
                #create sale order lines.
                self.create_sales_line(cr, uid, order, so_id, context)
            return True
        except Exception, e:
            _logger.debug('Sale Order %s' % (order['OrderNumber']))
            #TODO rollback
            _logger.error(
                'Error occurs when creating order!\n %s: %s' % (
                    type(e), str(e)))
            return False

    def automatic_payment_tradevine(self, cr, uid, ids, amount=None, context=None):
        """ Create the payment entries to pay a sale order, respecting
        the payment terms.
        If no amount is defined, it will pay the residual amount of the sale
        order. """
        if isinstance(ids, Iterable):
            assert len(ids) == 1, "one sale order at a time can be paid"
            ids = ids[0]
        sale = self.browse(cr, uid, ids, context=context)
        method = sale.payment_method_id
        if not method:
            raise osv.except_osv(
                _('Configuration Error'),
                _("An automatic payment can not be created for the sale "
                  "order %s because it has no payment method.") % sale.name)

        if not method.journal_id:
            #instead of error just return
            return False
            # raise osv.except_osv(
            #     _('Configuration Error'),
            #     _("An automatic payment should be created for the sale order %s "
            #       "but the payment method '%s' has no journal defined.") %
            #     (sale.name, method.name))

        journal = method.journal_id
        date = sale.date_order
        if amount is None:
            amount = sale.residual
        if sale.payment_term:
            term_obj = self.pool.get('account.payment.term')
            amounts = term_obj.compute(cr, uid, sale.payment_term.id,
                                       amount, date_ref=date,
                                       context=context)
        else:
            amounts = [(date, amount)]

        # reversed is cosmetic, compute returns terms in the 'wrong' order
        for date, amount in reversed(amounts):
            self._add_payment(cr, uid, sale, journal,
                              amount, date, sale.name, context=context)
        return True

    def automatic_payment(self, cr, uid, ids, amount=None, context=None):
        '''if the payment type is 26003 then skip this function'''
        if isinstance(ids, Iterable):
            assert len(ids) == 1, "one sale order at a time can be paid"
            ids = ids[0]
        sale = self.browse(cr, uid, ids, context=context)
        method = sale.payment_method_id
        if method.code in ('26003', '26001', '26008'):
            return False
        else:
            return super(sale_order, self).automatic_payment(
                cr, uid, ids, amount=amount, context=context)

    def create_payment_for_existing_SQ(self, cr, uid, ids, context=None):
        '''this is for temporary use.'''
        payment_method_pool = self.pool.get('payment.method')
        payment_method_ids = payment_method_pool.search(
            cr, uid, [('code', 'in', ['26003', '26001', '26008'])])
        sale_ids = self.search(
            cr, uid, [
                ('payment_method_id', 'in', payment_method_ids),
                ('state', '=', 'draft'),
                ('payment_ids', '=', False)])
        for sale in self.browse(cr, uid, sale_ids, context=context):
            print 'create prepayment for sale quotation: %s\n',sale.name
            sale.automatic_payment_tradevine(context=context)
            cr.commit()

    def sync_order(self, cr, uid, page_number, context=None):
        """sync order. create new SO and SOL

        Parameters
        ----------
        [page_number]: the page number of sale orders on tradevine.
        Returns
        -------
        True or False
        """
        tradevineUrl = self.generate_url(cr, uid, page_number, context)
        content = self.access_tradevine_api(cr, uid, tradevineUrl, context)
        result = json.load(content)
        total_count = result["TotalCount"]
        page_size = result["PageSize"]
        page_number = result["PageNumber"]
        _logger.debug(
            "***TotalCount:%d PageSize:%d"
            " PageNumber:%d " % (total_count, page_size, page_number))
        for order in result['List']:
            #check customerID and sale order line.
            if self._check_order(order):
                self.create_write_order(cr, uid, order, context)
            #remove this after finishing test.
            #return True
        if total_count > page_size * page_number:
            page_number += 1
            self.sync_order(cr, uid, page_number, context)
        return True

    def _check_order(self, order):
        return (order['CustomerID'] and order['SalesOrderLines'])

    def _order_receive_from_tradevine(self, cr, uid, context=None):
        """this method is main func that sync orders.
        used in cron job.

        Parameters
        ----------

        Returns
        -------

        """
        try:
            _logger.debug("***plugin_tradevine syncing order...")
            page_number = 1
            self.sync_order(cr, uid, page_number, context)
            return True
        except Exception, e:
            _logger.error(
                'Error occurs when sync order!\n Error: %s' % str(e))

    _columns = {
        'tv_order_number': fields.char('Tradevine Order Number', size=64),
        'tradevine_so_id': fields.char('Tradevine SO Id', size=64),
        'tradevine_org_id': fields.char('Tradevine Organization Id', size=64),
        'req_shipping_date': fields.datetime('Requested Shipping Date'),
        'external_notes': fields.text('External Notes'),
        'completed_date': fields.datetime('Completed Date'),
        'billing_address': fields.text('Billing Address'),
        'shipping_address': fields.text('Shipping Address'),
        'terms_of_trade': fields.selection(
            [('4000', 'Immediate'),
             ('4001', 'Cash'),
             ('4002', '7 days'),
             ('4003', '20th of month following invoice'),
             ('4004', '14 days'),
             ('4005', '21 days'),
             ('4006', '28 days'),
             ('4007', '30 days'),
             ('4008', '60 days'),
             ('4009', '90 days')],
            'Terms of Trade'),
        'payment_due_date': fields.datetime('Payment Due Date'),
        'payment_date': fields.datetime('Payment Date'),
        'is_payment_received': fields.boolean('Payment Received'),
        'payment_type': fields.selection(
            [('26001', 'Cash'),
             ('26002', 'Bank Transfer'),
             ('26003', 'Credit Card'),
             ('26004', 'Cheque'),
             ('26005', 'Escrow'),
             ('26006', 'Other'),
             ('26007', 'PayPal'),
             ('26008', 'EFTPOS')],
            'Payment Type'),
        'shipping_type': fields.selection(
            [('25001', 'Collection'),
             ('25002', 'Post'),
             ('25003', 'Courier'),
             ('25004', 'Free Shipping'),
             ('25005', 'Own Transport')],
            'Shipping Type'),
    }


class account_tax(osv.osv):
    _inherit = 'account.tax'
    _columns = {
        'tradevine_tax_id': fields.char('Tradevine tax id', size=64)
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
