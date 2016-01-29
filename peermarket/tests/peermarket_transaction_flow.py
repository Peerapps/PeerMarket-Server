import sys
import os
sys.path.append('../../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'peerapps.settings'
import django
django.setup()
from peermarket.errors import PeercoinError, PeerMarketError
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
from bitcoin.rpc import Proxy as rpcProcessedProxy
import external_db
import helpers, blockchain_func
#from django.test import TestCase
import json

def create_listing():
    from_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"
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
    submit_api_call(from_address, payload)

def update_listing():
    from_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"
    payload = json.dumps([
        {
            'action': 'update_listing',
            'category': 'Neopets2',
            'subcategory': 'Neopoints2',
            'listing_tx_id': 'MISSING',
            'quantity': '2222',
            'requested_peercoin': '22',
            'message': "I'm a second message on a listing!"
        }
    ])
    submit_api_call(from_address, payload)

def create_offer():
    from_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"
    payload = json.dumps([
        {
            'action': 'new_offer',
            'listing_tx_id': 'MISSING',
            'quantity': '1000000',
            'offered_peercoin': '10',
            'message': "I'm interested, let's do it. If chosen, I'll contact you on signal."
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
    blockchain_func.submit_opreturn(rpc_raw, rpc_processed, from_address, op_return_data)

    print "success"

create_listing()
create_offer()