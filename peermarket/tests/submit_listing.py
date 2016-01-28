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
from django.test import TestCase

'''
def submit_transactions(request):
    """
        request.POST = {
            "transactions": "[
            {
                'peercoin_address': '',
                'raw_transaction': '',
                'signed': '',
                'payload': ''
            },
            {
                ...
            }
            ]"
        }
    """
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')
'''


from_address = "mndvZGbYdUCWTC3JYP2eyvJEHxYLds4UWn"
message = "Test message to post to blockchain"
rpc_raw = rpcRawProxy(helpers.get_rpc_url())

#rpc_raw.walletpassphrase(request.POST['wallet_passphrase'], 60)

try:
    message += "|" + helpers.sign_string(rpc_raw, message, from_address)
except JSONRPCException, e:
    if "passphrase" in e.error['message']:
        raise PeercoinError("Wallet locked.")
    else:
        raise PeercoinError("Error while trying to sign with peercoin public key.")

print "Message plus signature:", message

#create a json structure to be posted externally
final_output = helpers.format_outgoing(message)

print "final_output", final_output

opreturn_key = external_db.post_data(final_output)

op_return_data = "pm" #program code (peermessage), 2 chars
op_return_data += opreturn_key #key pointing to external datastore

print "op_return_data", op_return_data

rpc_processed = rpcProcessedProxy()
blockchain_func.submit_opreturn(rpc_raw, rpc_processed, from_address, op_return_data)

print "success"