import sys
import os
sys.path.append('../../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'peerapps.settings'
import django
django.setup()
from peermarket.errors import PeercoinError
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
from bitcoin.rpc import Proxy as rpcProcessedProxy
import external_db
import helpers, blockchain_func
#from django.test import TestCase
import json

def new_listing(from_address):
    payload = json.dumps([
        {
            'action': 'new_listing',
            'category': 'Neopets',
            'subcategory': 'Neopoints',
            'quantity': '1000000',
            'requested_peercoin': '10',
            'message': "The exchange will be made like so: You create a Neopets trade, I'll bid the currency on it, you accept. Contact me via Signal @ 212 867 5309"
        }
    ])
    return submit_api_call(from_address, payload)

def update_listing(from_address, listing_tx_id):
    payload = json.dumps([
        {
            'action': 'update_listing',
            'category': 'Neopets2',
            'subcategory': 'Neopoints2',
            'listing_tx_id': listing_tx_id,
            'quantity': '2222',
            'requested_peercoin': '22',
            'message': "I'm a second message on a listing!"
        }
    ])
    submit_api_call(from_address, payload)

def new_offer(from_address, listing_tx_id):
    payload = json.dumps([
        {
            'action': 'new_offer',
            'listing_tx_id': listing_tx_id,
            'quantity': '1000000',
            'offered_peercoin': '10',
            'message': "I'm interested, let's do it. If chosen, I'll contact you on signal."
        }
    ])
    return submit_api_call(from_address, payload)

def update_offer(from_address, offer_tx_id):
    payload = json.dumps([
        {
            'action': 'update_offer',
            'offer_tx_id': offer_tx_id,
            'quantity': '1000000',
            'offered_peercoin': '11',
            'message': "I upped my offer because I really want your thing."
        }
    ])
    submit_api_call(from_address, payload)

def cancel_offer(from_address, offer_tx_id):
    payload = json.dumps([
        {
            'action': 'cancel_offer',
            'offer_tx_id': offer_tx_id
        }
    ])
    submit_api_call(from_address, payload)

def reject_offer(from_address, offer_tx_id):
    payload = json.dumps([
        {
            'action': 'reject_offer',
            'offer_tx_id': offer_tx_id,
            'message': "Raise it to 20 peercoins and you've got a deal."
        }
    ])
    submit_api_call(from_address, payload)

def accept_offer(from_address, offer_tx_id):
    payload = json.dumps([
        {
            'action': 'accept_offer',
            'offer_tx_id': offer_tx_id,
            'message': "Raise it to 20 peercoins and you've got a deal."
        }
    ])
    submit_api_call(from_address, payload)

def submit_api_call(from_address, payload):
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    #rpc_raw.walletpassphrase(request.POST['wallet_passphrase'], 60)

    try:
        payload += "|" + helpers.sign_string(rpc_raw, payload, from_address)
    except JSONRPCException, e:
        if "passphrase" in e.error['message']:
            raise PeercoinError("Wallet locked.")
        else:
            raise PeercoinError("Error while trying to sign with peercoin public key.")

    print "Payload plus signature:", payload

    formatted_payload = helpers.format_outgoing(payload)

    print "formatted_payload", formatted_payload

    opreturn_key = external_db.post_data(formatted_payload)

    op_return_data = "pm" #program code (peermarket), 2 chars
    op_return_data += opreturn_key #key pointing to external datastore

    print "op_return_data", op_return_data

    rpc_processed = rpcProcessedProxy()
    tx_id = blockchain_func.submit_opreturn(rpc_raw, rpc_processed, from_address, op_return_data)

    print "success"
    return tx_id

seller_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"
buyer_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"

try:
    listing_tx_id = new_listing(seller_address)
    update_listing(seller_address, listing_tx_id)

    offer_tx_id = new_offer(buyer_address, listing_tx_id)
    update_offer(buyer_address, offer_tx_id)
    offer_tx_id = new_offer(buyer_address, listing_tx_id)
    cancel_offer(buyer_address, offer_tx_id)
    offer_tx_id = new_offer(buyer_address, listing_tx_id)
    reject_offer(seller_address, offer_tx_id)
    offer_tx_id = new_offer(buyer_address, listing_tx_id)
    accept_offer(seller_address, offer_tx_id)
except Exception as e:
    if 'Connection refused' in str(e):
        raise PeercoinError('Unable to detect Peercoin wallet - are you sure the wallet is running?')
    else:
        raise