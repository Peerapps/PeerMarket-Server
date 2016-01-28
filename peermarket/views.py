from django.shortcuts import render
from django.http import HttpResponse
import json
from django.db.models import Q

import helpers, blockchain_func
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
import external_db

def submit_transactions(request):
    """
        request.POST = "{
            "transactions": [
            {
                'peercoin_address': '',
                'raw_transaction': '',
                'signed': '',
                'payload': ''
            },
            {
                ...
            }
            ]
        }"
    """
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

def get_listings(request):
    """
        request.POST = {
            "category": "",
            "subcategory": "",
            "listing_peercoin_address": "",
            "offer_peercoin_address": "",
            "starting_block": "",
            "listing_id": "",
            "include_offers": ""
        }

        #Returns listing information filtered by input, and offer information if requested.
    """
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

def get_transaction(request):
    """
        request.POST = {
            "tx_id": ""
        }

        #Returns full transaction info (payload, peercoin address, block number, raw transaction, signature)
    """
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

def get_blockchain_data(request):
    """
        request.POST = {
            "starting_block_id": ""
        }

        #Returns full transaction info (payload, peercoin address, block number, raw transaction, signature)
        from all blocks beyond optional starting_block_id.
    """
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')
