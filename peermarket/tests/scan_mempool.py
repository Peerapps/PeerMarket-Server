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

rpc_raw = rpcRawProxy(helpers.get_rpc_url())
blockchain_func.scan_block(rpc_raw, scan_mempool_only=True)