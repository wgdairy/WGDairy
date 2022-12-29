# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, Warning,UserError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
import requests
import json
import xmltodict
# import xml2json
import lxml.etree as ET
from datetime import datetime


class PosPaymentScreenConfig(models.Model):
	_name = 'pos.payment.screen.config'
	_rec_name = 'related_id'

	url = fields.Text(string="Customer Display Url",compute="compute_url")
	# show_rating_on_page = fields.Boolean(string="Show Rating On Page")
	welcome_screen_content = fields.Text(string="Welcome Screen")
	welcome_screen_heading = fields.Char(string="Welcome Screen Title",default="WELCOME")
	welcome_screen_subheading = fields.Char(string="Welcome Screen SubHeading")
	related_id = fields.Many2one('pos.config',string="Pos Config")
	type_of_screen = fields.Selection([('welcome','Welcome Screen'),('payment','Payment')],string="Type Of Screen")
	# payment_amount = fields.Float(string="Payment Amount")
	# ip_address = fields.Char(string="IP Address")
	is_update = fields.Boolean(string="Is Updated")
	promotions_pictures = fields.One2many('promotion.image','promotions_related_id',string="Promotional Pictures")

	@api.depends('related_id')
	def compute_url(self):
		for self_obj in self:
			data = request.httprequest.host_url
			url = '{}pos/payment/{}/screen'.format(data,self_obj.related_id.id)
			self_obj.url = url

	@api.constrains('related_id')
	def validate_configs(self):
		records = self.search([])
		count = 0
		for record in records:
			if record.related_id == self.related_id:
				count += 1
		if(count >1):
			raise ValidationError("You can't have two same pos configs.")


	@api.constrains('promotions_pictures')
	def validate_promotional_pics(self):
		if(self.promotions_pictures and len(self.promotions_pictures) > 3):
			raise ValidationError("You can't set more than 3 promotional pictures.")


	def redirect_customer_screen(self):
		base_url = request.httprequest.host_url
		url = '{}pos/payment/{}/screen'.format(base_url,self.related_id.id)
		return {
				"type": "ir.actions.act_url",
				"url": url,
				"target": "new",
				}

	@api.model
	def update_screen_info(self,config_id):
		_logger.info("************cofnig_id********:%r",config_id)
		config = self.browse(config_id)
		config.write({'is_update':False})


	@api.model
	def update_screen_on_pos(self,config_id):
		_logger.info("************cofnig_id********:%r",config_id)
		config = self.browse(config_id)
		config.write({
			'is_update':True,
			'type_of_screen':'welcome'
		})
	# def write(self, vals):
	# 	_logger.info("********Vals*****:%r",self.read([]))
	# 	opened_session = self.related_id.mapped('session_ids').filtered(lambda s: s.state != 'closed')
	# 	if opened_session:
	# 		raise UserError(_('Unable to modify this PoS Screen Configuration because there is an open PoS Session based on it.'))
	# 	result = super(PosPaymentScreenConfig, self).write(vals)
	# 	return result


class Promotions(models.Model):
	_name = 'promotion.image'

	image = fields.Binary(string="Promotional Pictures")
	promotions_related_id = fields.Many2one('pos.payment.screen.config',string="Promotions")

class PosConfig(models.Model):
	_inherit = 'pos.config'

	type_of_payment_screen = fields.Selection([('pos','Pos Payment'),('screen','On Payment Screen')],string="Type Of Payment Screen",default="screen")
	pos_payment_screen = fields.One2many('pos.payment.screen.config','related_id', string="Pos Review Screen")


	def open_screen_configuration(self):
		view_id_tree = self.env.ref('pos_connect2_payment_acquirer.pos_screen_conf_form').id
		if self.pos_payment_screen and self.pos_payment_screen.id:
			return {
				'type': 'ir.actions.act_window',
				'res_model': 'pos.payment.screen.config',
				'view_mode': 'form',
				'res_id':self.pos_payment_screen.id,
				'view_id':view_id_tree,
				'target': 'current'
			}
		else:
			raise Warning("No Payment Screen Settings available for this POS.")

class ConnectTwo(models.Model):
	_name = "pos.connect.two"


	def get_disclosure(self):
		return self.env['pos_connect2.configuration'].search([('active_record','=',True)],limit=1).john_deere_financial_legal_invoice_disclosure


	def capture_request_message(self,config_id,args):

		token = args['token_no']
		order_line=False
		card_number = args['card_number']
		inv_amount = args['inv_amount']
		order_no = args['order_no']
		order=""
		date_now = datetime.now()
		date_now = str(date_now.date())+'T'+str(date_now.time())[0:12]

		if 'order_line' in args:
			order_line = args['order_line']


		xml = """<?xml version="1.0" encoding="UTF-8"?> 
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"> <SOAP-ENV:Header> 
 <Service>PointOfSale</Service> 
 <Activity>Capture</Activity> 
 <SourceSystem>Connect2</SourceSystem> 
 <SourceID>1000</SourceID> 
 <ISFmsgVersion>odoo-15</ISFmsgVersion> 
 <ActivityMsgVersion>odoo-15</ActivityMsgVersion> 
 <Locale>en_US</Locale> 
 <TimeStamp/> 
</SOAP-ENV:Header> 
<SOAP-ENV:Body> 
 <POS:PointOfSale xmlns:POS="http://pos.jdc.deere.com/xml" POS:version="" POS:vendor="">  <POS:amount>"""+str(inv_amount)+"""</POS:amount> 
 <POS:saleDate>"""+str(date_now)+"""</POS:saleDate> 
 <POS:productLine>Farm Plan</POS:productLine> 
 <POS:merchant> 
 <POS:terminalNumber>"""+str(config_id.terminal_number)+"""</POS:terminalNumber>  <POS:merchantNumber>"""+str(config_id.merchant_number)+"""</POS:merchantNumber> 
 <POS:invoiceNumber>"""+str(order_no)+"""</POS:invoiceNumber> 
 <POS:purchaseOrderNumber/> 
 </POS:merchant> 
 <POS:customer> 
 <POS:card> 
 <POS:cardNumber>"""+str(card_number)+"""</POS:cardNumber> 
 <POS:cardType>Farm Plan</POS:cardType> 
 </POS:card> 
 <POS:patronNumber/> 
 </POS:customer> 
 <POS:creditPlan> 
 <POS:creditPlanNumber>"""+str(config_id.credit_plan_number)+"""</POS:creditPlanNumber> 
 <POS:descriptiveBillingCode>"""+str(args['dbc_code'])+"""</POS:descriptiveBillingCode>  <POS:serialNumber/> 
 <POS:modelNumber/> 
 </POS:creditPlan> 
 <POS:authorization> 
 <POS:authorizationNumber>"""+str(token)+"""</POS:authorizationNumber>  
 </POS:authorization>  
<POS:lineItems>"""

		if order_line:
			for o_id in order_line:
				unit_price = float(o_id['price'])
				quantity = float(o_id['quantity'])
				sub_total = unit_price*quantity

				order+= """<POS:lineItem POS:description="""+'"'+ o_id['product']+'"'+""" POS:manufactureName="" POS:mfgPartNumber="" POS:numberOfUnits="""+'"'+ str(quantity)+'"'+""" POS:unitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:unitPrice="""+'"'+ str(unit_price)+'"'+""" POS:pricingUnitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:skuNumber="""+'"'+str(o_id['product'])+'"'+""" POS:upc="" POS:lineItemTotal="""+'"'+str(sub_total)+'"'+"""/>"""



		else:
			order = """<POS:lineItem POS:description="Customer Invoice" POS:manufactureName="" POS:mfgPartNumber="" POS:numberOfUnits="2.5" POS:unitOfMeasure="Hours" POS:unitPrice="60" POS:pricingUnitOfMeasure="Hour" POS:skuNumber="" POS:upc="" POS:lineItemTotal="150.00"/></POS:lineItems></POS:PointOfSale></SOAP-ENV:Body></SOAP-ENV:Envelope>"""  
 

		end = """</POS:lineItems></POS:PointOfSale></SOAP-ENV:Body></SOAP-ENV:Envelope> """
		return xml+order+end

		

	def get_config_details(self,session_pos):
		print (self.env['pos_connect2.configuration'].search([('active_record','=',True),('session_id','=',session_pos)],limit=1),"lklklklklklklklklklklklklklklklklklkkk9999999")
		return self.env['pos_connect2.configuration'].search([('active_record','=',True),('session_id','=',session_pos)],limit=1)

	def get_api_url(self,session_pos):
		return self.env['pos_connect2.configuration'].search([('active_record','=',True),('session_id','=',session_pos)],limit=1).api_url

	def call_api(self,xml,session_pos):
		
		response =False

		try:
			# url = 'https://connect2cert.deere.com/POS/services/TransactionBroker'
			url = self.get_api_url(session_pos)
			parser = ET.XMLParser(recover=True)
			headers = {'Content-Type': 'application/xml'}
			response=requests.post(url, data=xml, headers=headers)
		except:
			raise Warning('Something went wrong')

		return response


	@api.model
	def get_partner_card(self,args,**kwargs):


		partner_id=self.env['res.partner'].search([('id','=',args['partner_id'])])


		return {'card_number':partner_id.card_number,'name':partner_id.name}


	@api.model
	def api_call_for_review_data(self,args,**kwargs):

		tr_status = False
		config_id = self.get_config_details()
		xml =  self.capture_request_message(config_id,args)
		response =self.call_api(xml,args['config_id'])
		if response:
			if response.status_code == 200:
				data_val = response.content
				data_json_str=json.dumps(xmltodict.parse(data_val))
				data_json = json.loads(data_json_str)
				print ("data review===============",data_json)

				try:
					if 'SOAP-ENV:Envelope' in data_json:
						if 'SOAP-ENV:Body' in data_json['SOAP-ENV:Envelope']:
							if 'SOAP-ENV:Fault' in data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']:
								tr_status = "Failure"
							else:
								
								tr_status = "Success"



				except:
					raise Warning('Something went wrong')

		return tr_status

	@api.model
	def api_call_for_data_transfer(self,args,**kwargs):


		order_no =False
		tr_status ="Success"
		purchase =False
		credit =False
		xml=False
		customer =''
		payment_type =''
		order_line =False
		dbc_code = args['dbc_code']
		session_pos = args['config_id']
		
		config_id = self.get_config_details(session_pos)
		if 'order_line' in args:
			order_line = args['order_line']
		


		card_number =args['card-element']

		
		inv_amount = args['invoice_amount']
		pos_id = self.env['pos.order'].search([('name','=',args['order_no'])])

		# get the invoice number from invoice and pos
		if 'inv_payment' not in args:
			# if not args['inv_payment']:

			order_no = args['order_no'].split()
			order_no = order_no[1]
		else:
			order_no = args['order_no']


		
		if str(args['check']) == 'True':

			partner_id=self.env['res.partner'].search([('id','=',args['partner_id'])])
			if partner_id:
				partner_id.write({'card_number':card_number})
				customer = partner_id.id

		
		if int(inv_amount) <0:
			xml = self.credit_request_message(card_number,config_id,float(inv_amount)*-1,order_no,order_line,dbc_code)
			credit=True
		else:
			xml = self.purchase_request_message(card_number,config_id,inv_amount,order_no,order_line,dbc_code)
			purchase=True



		response =self.call_api(xml,session_pos)



		if response and response.status_code == 200:

				data_val = response.content
				data_json_str=json.dumps(xmltodict.parse(data_val))
				data_json = json.loads(data_json_str)
				print ("1111111",data_json)

				# credit, purchase and review checking
				try:
					if 'SOAP-ENV:Envelope' in data_json:
						if 'SOAP-ENV:Body' in data_json['SOAP-ENV:Envelope']:
							if 'SOAP-ENV:Fault' in data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']:
								tr_status = "Failure"
							else:
								if purchase:
									if data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']['POS:PointOfSale']['POS:statusCode'] == 'Approved':

										tr_status = "Success"
										payment_type = "Purchase"

									elif data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']['POS:PointOfSale']['POS:statusCode'] == 'Review':
										tr_status ='Review'
										tr_status = data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']['POS:PointOfSale']['POS:statusMessage']
										payment_type = "Purchase Review"
									elif data_json['SOAP-ENV:Envelope']['SOAP-ENV:Body']['POS:PointOfSale']['POS:statusCode'] == 'Declined':
										tr_status ="Failure"
										payment_type = "Purchase Declied"

									else :
										tr_status = "Failure"
										payment_type = "Purchase"

								elif credit:
									tr_status = "Success"
									payment_type = "Credit"




				except:
					raise Warning('Something went wrong')

				if tr_status =="Success":
					tr_msg ="Success"
				else:
					tr_msg = "Failure"
					

				vals={'tr_status': tr_status, 'inv_amount':inv_amount,'payment_type':payment_type,'customer':customer,'invoice_no':order_no
				,'card_number':card_number[-4:],'dbc_code':dbc_code,'credit_plan_number':config_id.credit_plan_number,'authorization_no':'','reference_no':''}

				self.env['pos.connect.transaction'].create(vals)
		
		else:
			raise Warning(f"Hello person, there's a {response} error with your request")

		return tr_status

	def credit_request_message(self,card_number,config_id,inv_amount,order_no,order_line,dbc_code):

		order=""
		date_now = datetime.now()
		date_now = str(date_now.date())+'T'+str(date_now.time())[0:12]

		xml = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header>
<Service>PointOfSale</Service>
<Activity>Credit</Activity>
<SourceSystem> Connect2</SourceSystem>
<SourceID>1000</SourceID>
<ISFmsgVersion>2.0</ISFmsgVersion>
<ActivityMsgVersion>1.0</ActivityMsgVersion>
<Locale>en_US</Locale>
<TimeStamp/>
</SOAP-ENV:Header>
<SOAP-ENV:Body>
<POS:PointOfSale xmlns:POS="http://pos.jdc.deere.com/xml" POS:version="" POS:vendor="">
<POS:amount>"""+str(inv_amount)+"""</POS:amount>
<POS:saleDate>"""+str(date_now)+"""</POS:saleDate>
<POS:productLine>Farm Plan</POS:productLine>
<POS:merchant>
<POS:terminalNumber>"""+str(config_id.terminal_number)+"""</POS:terminalNumber>
<POS:merchantNumber>"""+str(config_id.merchant_number)+"""</POS:merchantNumber>
<POS:invoiceNumber>"""+str(order_no)+"""</POS:invoiceNumber>
<POS:originalInvoiceNumber>"""+str(order_no)+"""</POS:originalInvoiceNumber>
<POS:purchaseOrderNumber/>
</POS:merchant>
<POS:customer>
<POS:card>
<POS:cardNumber>"""+str(card_number)+"""</POS:cardNumber>
<POS:cardType>Farm Plan</POS:cardType>
</POS:card>
<POS:patronNumber/>
</POS:customer>
<POS:creditPlan>
<POS:creditPlanNumber>"""+str(config_id.credit_plan_number)+"""</POS:creditPlanNumber>
<POS:descriptiveBillingCode>"""+str(dbc_code)+"""</POS:descriptiveBillingCode>
<POS:serialNumber/>
<POS:modelNumber/>
</POS:creditPlan>
<POS:lineItems>
"""
		if order_line:
			for o_id in order_line:
				unit_price = float(o_id['price'])
				quantity = float(o_id['quantity'])
				sub_total = unit_price*quantity

				order+= """<POS:lineItem POS:description="""+'"'+ o_id['product']+'"'+""" POS:manufactureName="" POS:mfgPartNumber="" POS:numberOfUnits="""+'"'+ str(quantity)+'"'+""" POS:unitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:unitPrice="""+'"'+ str(unit_price)+'"'+""" POS:pricingUnitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:skuNumber="""+'"'+str(o_id['product'])+'"'+""" POS:upc="" POS:lineItemTotal="""+'"'+str(sub_total)+'"'+"""/>"""



		else:
			order = """
<POS:lineItem POS:description="Round Up 235z" POS:manufactureName="Monsanto"
POS:mfgPartNumber="" POS:numberOfUnits="1" POS:unitOfMeasure="Pounds"
POS:unitPrice"""+'"'+str(inv_amount)+'"'+""" POS:pricingUnitOfMeasure="Ton" POS:skuNumber="54654654"
POS:upc="" POS:lineItemTotal="""+'"'+str(inv_amount)+'"'+"""/>"""

		end = """</POS:lineItems></POS:PointOfSale></SOAP-ENV:Body></SOAP-ENV:Envelope> """
		return xml+order+end
      
	

	def purchase_request_message(self,card_number,config_id,inv_amount,order_no,order_line,dbc_code):

		order=""
		date_now = datetime.now()
		date_now = str(date_now.date())+'T'+str(date_now.time())[0:12]


		xml = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header>
<Service>PointOfSale</Service>
<Activity>Purchase</Activity>
<SourceSystem> Connect2</SourceSystem>
<SourceID>1000</SourceID>
<ISFmsgVersion>2.0</ISFmsgVersion>
<ActivityMsgVersion>1.0</ActivityMsgVersion>
<Locale>en_US</Locale>
<TimeStamp/>
</SOAP-ENV:Header>
<SOAP-ENV:Body>
<POS:PointOfSale xmlns:POS="http://pos.jdc.deere.com/xml" POS:version="" POS:vendor="">
<POS:amount>"""+str(inv_amount)+"""</POS:amount>
<POS:saleDate>"""+str(date_now)+"""</POS:saleDate>
<POS:productLine>Farm Plan</POS:productLine>
<POS:merchant>
<POS:terminalNumber>"""+str(config_id.terminal_number)+"""</POS:terminalNumber>
<POS:merchantNumber>"""+str(config_id.merchant_number)+"""</POS:merchantNumber>
<POS:invoiceNumber>"""+str(order_no)+"""</POS:invoiceNumber>
<POS:purchaseOrderNumber/>
</POS:merchant>
<POS:customer>
<POS:card>
<POS:cardNumber>"""+str(card_number)+"""</POS:cardNumber>
<POS:cardType>Farm Plan</POS:cardType>
</POS:card>
<POS:patronNumber/>
</POS:customer>
<POS:creditPlan>
<POS:creditPlanNumber>"""+str(config_id.credit_plan_number)+"""</POS:creditPlanNumber>
<POS:descriptiveBillingCode>"""+str(dbc_code)+"""</POS:descriptiveBillingCode>
<POS:serialNumber/>
<POS:modelNumber/>
</POS:creditPlan>
<POS:lineItems>"""
		if order_line:
			for o_id in order_line:
				unit_price = float(o_id['price'])
				quantity = float(o_id['quantity'])
				sub_total = unit_price*quantity

				order+= """<POS:lineItem POS:description="""+'"'+ o_id['product']+'"'+""" POS:manufactureName="" POS:mfgPartNumber="" POS:numberOfUnits="""+'"'+ str(quantity)+'"'+""" POS:unitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:unitPrice="""+'"'+ str(unit_price)+'"'+""" POS:pricingUnitOfMeasure="""+'"'+ str(o_id['uom'][0])+'"'+""" POS:skuNumber="""+'"'+str(o_id['product'])+'"'+""" POS:upc="" POS:lineItemTotal="""+'"'+str(sub_total)+'"'+"""/>"""



		else:
			order = """<POS:lineItem POS:description="Tax" POS:manufactureName="" POS:mfgPartNumber="" POS:numberOfUnits="1" POS:unitOfMeasure="" POS:unitPrice="""+'"'+str(inv_amount)+'"'+""" POS:pricingUnitOfMeasure="" POS:skuNumber="" POS:upc="" POS:lineItemTotal="""+'"'+str(inv_amount)+'"'+"""/>"""

		end = """</POS:lineItems></POS:PointOfSale></SOAP-ENV:Body></SOAP-ENV:Envelope>"""
		return xml+order+end

	