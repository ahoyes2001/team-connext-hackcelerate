"""
Telegram Bot for ChatOut Hackcelerate Software

Bot accepts order information and pushes it to main application's RESTful API interface

Team ConNext - Jordan Barrett and Andrew Hoyes

"""
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import requests as re
import json

#first URL is the main page of the application
URL = "http://d2e3836d6a4d.ngrok.io/"
#second URL is the api link for the applicatino
URL2 = "http://d2e3836d6a4d.ngrok.io/api"
headers = {'content-type': 'application/json'}
UPDATER = Updater(token='961559315:AAFyDi_RamZGQ3Tggy_8LahUSZAjbXWQcWQ', use_context=True)
DISPATCHER = UPDATER.dispatcher

PRODUCT, QUANTITY, NAME, ADDRESS, PHONE, DELIVERY, CONFIRMATION, CHANGE_MENU = range(8)

ORDER_DICT = {}
PRODUCT_DICT = {1:"Clark's Desert Boot - $9500.00 JMD", 2:"Nike Air Force 1 - $4300.00 JMD", 3:"Adidas Yeezy Boost 350 - $19450.00 JMD", 4:"Fila Disruptor - $5400.00 JMD", 5:"Reebok Sneaker - $1900.00 JMD"}

def start(update, context):
	update.message.reply_text("Hi thanks for reaching out to our store. To start your order please select the product you'd like to purchase"
	, reply_markup=product_menu_keyboard())
	return PRODUCT

def getProduct(update, context):
	query = update.callback_query
	query.answer()
	ORDER_DICT["order"] = int(query.data)
	print(query.data)
	if "delivery_date" in ORDER_DICT:
		try:
			return confirm(update, context)
		except Exception as e: 
			print(e)
	query.edit_message_text(text="Great Choice! And how many would you like (1,2,3, etc)?")
	return QUANTITY

def getQuantity(update, context):
	ORDER_DICT["quantity"] = int(update.message.text)
	if "delivery_date" in ORDER_DICT:
		return confirm(update, context)
	update.message.reply_text("Thanks a lot. Can we have your name?")
	return NAME
	
def getName(update, context):
	ORDER_DICT["name"] = update.message.text
	if "delivery_date" in ORDER_DICT:
		return confirm(update, context)
	update.message.reply_text("Nice to meet you %s! What number can we reach you at?" % ORDER_DICT["name"])
	return PHONE

def getPhone(update, context):
	ORDER_DICT["contact"] = update.message.text
	if "delivery_date" in ORDER_DICT:
		return confirm(update, context)
	update.message.reply_text("Awesome, and can I get the address to deliver to?")
	return ADDRESS

def getAddress(update, context):
	ORDER_DICT["address"] = update.message.text
	if "delivery_date" in ORDER_DICT:
		return confirm(update, context)
	update.message.reply_text("Great! And finally, what date would you like for us to deliver on? (DD/MM/YYY)")
	return DELIVERY

def getTotal(product, quantity):
	data = {"id": product}
	data = json.dumps(data)
	req = re.post(URL2, data=data, headers=headers)
	response = json.loads(req.text)
	price = response["price"]
	return quantity*price
	
def confirm(update, context):
	total = getTotal(ORDER_DICT["order"], ORDER_DICT["quantity"])
	reply_keyboard = [['Yep', 'Nope']]
	confirmation_text = """
	Great! Now just to confirm your order:\n
	Item Name: %s\n
	Quantity: %s\n
	Name: %s\n
	Phone Number: %s\n
	Address: %s\n
	Delivery Date: %s\n
	Total due on Delivery: %0.2f JMD
	\n
	Is this information correct?
	""" % (PRODUCT_DICT[ORDER_DICT["order"]],ORDER_DICT["quantity"], ORDER_DICT["name"], ORDER_DICT["contact"], ORDER_DICT["address"], ORDER_DICT["delivery_date"], total )
	if update.callback_query:
		update.callback_query.edit_message_text(text=confirmation_text, reply_markup=confirm_menu_keyboard())
		return CONFIRMATION
	update.message.reply_text(confirmation_text, reply_markup=confirm_menu_keyboard())
	return CONFIRMATION

def getDelivery(update, context):
	ORDER_DICT["delivery_date"] = update.message.text
	return confirm(update, context)

def getConfirmation(update, context):
	query = update.callback_query
	query.answer()
	confirm = query.data
	if confirm == "Yep":
		try:
			data = json.dumps(ORDER_DICT)
			data = json.loads(data)
			data = str(data).replace("'",'"') #gwaan aga
			print (data)
			request = re.post(URL, data=data, headers=headers)
			query.edit_message_text(text="Thanks for choosing our store. We'll contact you again on the delivery date")
			ORDER_DICT.clear()
		except Exception as e:
			print (e)
		return ConversationHandler.END
	query.edit_message_text(text="Which item would you like to change?", reply_markup=change_menu_keyboard())
	return CHANGE_MENU

def changeMenu(update, context):
	query = update.callback_query
	query.answer()
	option = int(query.data)
	if option == PRODUCT:
		query.edit_message_text(text="Which product is it that you'd like?", reply_markup=product_menu_keyboard())
	elif option == PHONE:
		query.edit_message_text(text="What number can we reach you at?")
	elif option == NAME:
		query.edit_message_text(text="Could you give us your name?")
	elif option == DELIVERY:
		query.edit_message_text(text="What date would you like us to deliver? (DD/MM/YYY)")
	elif option == QUANTITY:
		query.edit_message_text(text="How many would you like?")
	return option

def cancel(update, context):
	return ConversationHandler.END
	
def main():
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],
		states = {
			PRODUCT: [CallbackQueryHandler(getProduct)],
			QUANTITY: [MessageHandler(Filters.text, getQuantity)],
			NAME: [MessageHandler(Filters.text, getName)],
			PHONE: [MessageHandler(Filters.text, getPhone)],
			ADDRESS: [MessageHandler(Filters.text, getAddress)],
			DELIVERY: [MessageHandler(Filters.text, getDelivery)],
			CONFIRMATION: [CallbackQueryHandler(getConfirmation)],
			CHANGE_MENU: [CallbackQueryHandler(changeMenu)]
		},
		#show total due at end of conversation as well as order details
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	DISPATCHER.add_handler(conv_handler)
	UPDATER.start_polling()
	UPDATER.idle()

	
def product_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Clark\'s Desert Boot - $9500.00 JMD', callback_data=1)],
              [InlineKeyboardButton('Nike Air Force 1 - $4300.00 JMD', callback_data=2)],
			  [InlineKeyboardButton('Adidas Yeezy Boost 350 - $19450.00 JMD', callback_data=3)],
			  [InlineKeyboardButton('Fila Disruptor - $5400.00 JMD', callback_data=4)],
              [InlineKeyboardButton('Reebok Sneaker - $1900.00 JMD', callback_data=5)]]
  return InlineKeyboardMarkup(keyboard)

def confirm_menu_keyboard():
	keyboard = [[InlineKeyboardButton("Yep", callback_data="Yep")],
				[InlineKeyboardButton("Nope", callback_data="Nope")]]
	return InlineKeyboardMarkup(keyboard)
	
def change_menu_keyboard():
	keyboard = [[InlineKeyboardButton("Product", callback_data=PRODUCT)],
				[InlineKeyboardButton("Quantity", callback_data=QUANTITY)],
				[InlineKeyboardButton("Name", callback_data=NAME)],
				[InlineKeyboardButton("Phone #", callback_data=PHONE)],
				[InlineKeyboardButton("Address", callback_data=ADDRESS)],
				[InlineKeyboardButton("Delivery Date", callback_data=DELIVERY)]]
	return InlineKeyboardMarkup(keyboard)

if __name__ == '__main__':
    main()