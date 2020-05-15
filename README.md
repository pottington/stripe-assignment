
# Alistair Pott – PaymentIntents assignment

This package contains the output of this exercise. I created a simple theoretical store inspired by the game Animal Crossing. I integrated PaymentIntents into that store.

## Contents
-   **store.html** – page on which user chooses items to buy
-   **checkout.html** – get card details and submit the charge
-   **client.js** – handle the exectin on the checkout page  
-   **server.py** – backend logic for store, checkout, and webhook
- **global.css** – example styling with some additions for my store

## Running the project

**1. Install the various dependencies** 
This is basically Flask and Stripe. I have no made any changes. 

```
pip3 install -r requirements.txt
```

**2. Start the CLI to forward webhooks**
Nothing special here either. This is the step in which you get the endpoint secret for line 13 of server.py

First connect to your Stripe account.
```
stripe login
```
Then start the CLI listening and forwarding
```
stripe listen --forward-to http://localhost:4242/webhook
```
Note the webhook signing secret that is return. 

**3. Update the API keys**
My submission includes my own test keys. You should replace them with yours.
```
client.js line 3
server.py line 12
server.py line 13 (webhook signing secret from previous step)
```

**4. Run the server**

```
export FLASK_APP=server.py
python3 -m flask run --port=4242
```

**4. Run the store and submit test charges**
Go to:  [http://localhost:4242/](http://localhost:4242/)

Set quantities of each fruit and then hit the "Buy!" button. Use the various test cards to submit payments. 

**5. Verify output orders**
When PaymentIntents are successfully charged the associated orders are written to the orders.txt file. 
