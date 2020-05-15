#! /usr/bin/env python3.6
"""
Python 3.6 or newer required.
"""
import json
import os
import stripe
from datetime import datetime

# Keys
# This is my test key, so you'll need to replace it (so that you can insert a listening CLI)
stripe.api_key = "sk_test_zVi7BF0UPB9tqBl30PGrhOIM00LBoILLMF"
# This will also need updating
endpoint_secret = "whsec_d4iTGuqsKijLm63VNobbFdZv645X82iu"

from flask import Flask, render_template, jsonify, request

app = Flask(__name__, static_folder=".",
            static_url_path="", template_folder=".")


FRUIT_PRICES = {
    'apples' : 100,
    'oranges': 150,
    'pears'  : 100,
    'peaches' : 200,
    'cherries': 300
}


# Grab the details from the form and structure an order
#    * For each fruit collect qty and price (for fulfillment)
#    * Also get the total charge for the order
def get_order_details(items):
    total = 0
    order = {}
    for fruit in items:
        total += FRUIT_PRICES[fruit] * int(items[fruit])
        order[fruit] = items[fruit] + " at " + str(FRUIT_PRICES[fruit])
    
    order['total'] = total

    return order


# 1. Start with the store page
#   * Renders a list of fruit inputs for quantities
@app.route('/')
def list_items():
    return render_template('store.html')


# 2. Show the checkout page
#   * Get the order information from POST
#   * Create a PaymentIntent
#   * Render the checkout page (including ClientSecret)
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    # Bail out if this is not POST
    if request.method != 'POST':
        return 'Go back to start'

    # Get the order details from the POST'ed form
    order = get_order_details(request.form)
    total = order['total']

    if total == 0:
        return 'Cart is empty'
    try:
        # Create the PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total,
            currency='usd',
            metadata=order   # Include the order for easy retrieval later
        )
        return render_template('checkout.html', 
            clientSecret=intent['client_secret'],  # Client will use this to submit the charge
            total = "${price:.2f}".format(price = total/100) # This is for display on the cart page
            )
    
    except Exception as e:
        return "Error creating PaymentIntent: " + str(e)

# 3. Then listen for Stripe to tell us that the payment went through
#    * Extract the event
#    * If it is a payment_intent.success then:
#         * Exctract the order from the payment intent metadata
#         * Write the order to orders.txt for fulfillment
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    
    event = None

    # Grab the event that is being sent back
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return "", 400
    except stripe.error.SignatureVerificationError as e:
        return "", 400


    # Handle the event
    if event.type == 'payment_intent.succeeded': # This is the one that we really care about
        # Get the PaymentIntent object out of the event
        payment_intent = event.data.object 

        # Write the order to our output file orders.txt
        #   * We saved the order into the PaymentIntent.metadata when we created it
        f = open("orders.txt","a")
        f.write(datetime.now().strftime("[%m/%d/%Y %H:%M:%S]") + "\n" + str(payment_intent.metadata) + "\n\n")
        f.close()

    elif event.type == 'payment_intent.created':
        print("PaymentIntent created.\n")
    elif event.type == 'charge.succeeded':
        print("Card was charged.\n")
    # ... handle other event types
    else:
        # Unexpected event type
        return "", 400

    return "", 200


if __name__ == '__main__':
    app.run()