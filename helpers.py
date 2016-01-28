import os
import gnupg #also install https://gpgtools.org/gpgsuite.html
import urllib
import datetime
from decimal import Decimal
import platform
from bitcoinrpc.authproxy import AuthServiceProxy
import external_db
import time
import peerapps.settings
import json
from peermarket.models import Listing, Offer, Message, Transaction

import shutil

def process_payload(transaction, payload_str):
    try:
        payload = json.loads(payload_str)
    except:
        raise ValueError('Unable to process json string from payload: '+payload_str)

    for db_query in payload:

        if 'action' not in db_query:
            raise ValueError('Unable to detect action requested in: '+str(db_query))

        if db_query['action'] == 'new_listing':
            listing_details = {
                "tx_id": transaction.tx_id,
                "category": db_query['category'],
                "subcategory": db_query['subcategory'],
                "quantity": db_query['quantity'],
                "requested_peercoin": db_query['requested_peercoin'],
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created
            }
            new_listing = Listing(**listing_details)
            new_listing.save()

            if db_query.get('message', ''):
                message_details = {
                    "tx_id": transaction.tx_id,
                    "listing_tx_id": transaction.tx_id,
                    "peercoin_address": transaction.peercoin_address,
                    "block_number_created": transaction.block_number_created,
                    "time_created": transaction.time_created,
                    "message": db_query['message']
                }
                new_message = Message(**message_details)
                new_message.save()
        else:
            raise ValueError('Unable to parse db_query requested in: '+str(db_query))

'''

{
    'action': 'new_listing',
    'peercoin_address': from_address,
    'category': 'Neopets',
    'subcategory': 'Neopoints',
    'quantity': '1000000',
    'requested_peercoin': '10',
    'message': "The exchange will be made like so: You create a Neopets trade, I'll bid the currency on it, you accept. Contact me via Signal @ 212 867 5309"
}
'''

def download_payload(rpc_raw, key, from_address):
    found_data = external_db.get_data(key)

    if not found_data:
        print "Unable to retrieve payload, skipping"
        return None

    formatted_message = format_incoming(found_data)
    try:
        verified_message = verify_and_strip_signature(rpc_raw, formatted_message, from_address)
    except AssertionError:
        print "Signature invalid, skip payload."
        return None
    except AttributeError:
        print "Unable to pull payload from external data source."
        return None

    return verified_message

def download_payloads(rpc_raw):
    transactions_waiting = Transaction.objects.filter(payload_retrieved=False).order_by('-time_created')
    for transaction in transactions_waiting:
        payload_str = download_payload(rpc_raw, transaction.pm_key, transaction.peercoin_address)
        print
        print "***Pulled new payload:", payload_str
        transaction.pm_payload = payload_str
        transaction.payload_retrieved = True
        transaction.save()
        process_payload(transaction, payload_str)
        #TODO Parse transaction details, look for db changes (e.g. new listings) and do those.

def get_service_status():
    """
        Retrieve user configuration, and status of wallet's rpc server, transaction index, and gpg's installation.
    """
    conf = get_config()
    if 'rpcpassword' in conf and conf['rpcpassword']:
        conf['rpcpassword'] = "*******"

    try:
        rpc_raw = AuthServiceProxy(get_rpc_url())
        rpc_raw.getblockcount()
        conf['wallet_connected_status'] = "good"
    except:
        conf['wallet_connected_status'] = "bad"

    try:
        if not os.path.exists(peerapps.settings.BASE_DIR+"/test_gpg_setup"):
            os.mkdir(peerapps.settings.BASE_DIR+"/test_gpg_setup")
        gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/test_gpg_setup")
        shutil.rmtree(peerapps.settings.BASE_DIR+"/test_gpg_setup", ignore_errors=True)
        conf['gpg_suite_installed'] = "good"
    except:
        conf['gpg_suite_installed'] = "bad"

    return conf

def edit_config(forced_updates, optional_updates=None):
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/PPCoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'PPCoin')
    else:
        btc_conf_file = os.path.expanduser('~/.ppcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'ppcoin.conf')

    new_file_contents = ""

    # Extract contents of ppcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # PPCoin Core accepts empty rpcuser, not specified in btc_conf_file
        for line in fd.readlines():
            orig_line = line
            if '=' not in line:
                new_file_contents += orig_line
                continue
            if '#' in line:
                line = line[:line.index('#')]
            k, v = line.split('=', 1)
            if k in forced_updates:
                new_file_contents += k + "=" + forced_updates[k] + "\n"
                del forced_updates[k]
            elif optional_updates and k in optional_updates:
                new_file_contents += orig_line.strip() + "\n"
                del optional_updates[k]
            else:
                new_file_contents += orig_line
        new_file_contents += "\n"
        for k,v in forced_updates.items():
            new_file_contents += k + "=" + v + "\n"
        if optional_updates:
            for k,v in optional_updates.items():
                new_file_contents += k + "=" + v + "\n"

    with open(btc_conf_file, 'w') as fd:
        fd.write(new_file_contents)

def get_config():
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/PPCoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'PPCoin')
    else:
        btc_conf_file = os.path.expanduser('~/.ppcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'ppcoin.conf')

    # Extract contents of ppcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # PPCoin Core accepts empty rpcuser, not specified in btc_conf_file
        conf = {'rpcuser': ""}
        for line in fd.readlines():
            if '#' in line:
                line = line[:line.index('#')]
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            conf[k.strip()] = v.strip()

        conf['rpcport'] = int(conf.get('rpcport', -1))
        conf['rpcssl'] = conf.get('rpcssl', '0')

        if conf['rpcssl'].lower() in ('0', 'false'):
            conf['rpcssl'] = False
        elif conf['rpcssl'].lower() in ('1', 'true'):
            conf['rpcssl'] = True
        else:
            raise ValueError('Unknown rpcssl value %r' % conf['rpcssl'])

    if conf['rpcport'] == -1:
        if 'testnet' in conf and conf['testnet'] in ['1', 'true']:
            conf['rpcport'] = 9904
        else:
            conf['rpcport'] = 9902

    conf['file_loc'] = btc_conf_file
    return conf

def get_rpc_url():
    conf = get_config()
    if 'rpcpassword' not in conf:
        raise ValueError('The value of rpcpassword not specified in the configuration file.')
    service_url = ('%s://%s:%s@localhost:%d' %
        ('https' if conf['rpcssl'] else 'http',
         conf['rpcuser'], conf['rpcpassword'],
         conf['rpcport']))
    return service_url

def format_outgoing(plaintext):
    return urllib.quote_plus(plaintext.encode("base64"))

def format_incoming(plaintext):
    try:
        return urllib.unquote_plus(plaintext).decode("base64")
    except:
        return None

def sign_string(rpc_connection, plaintext, address):
    return rpc_connection.signmessage(address, plaintext)

def verify_and_strip_signature(rpc_connection, plaintext, address):
    base = plaintext.split("|")
    signature = base.pop()
    message = "|".join(base)
    assert rpc_connection.verifymessage(address, signature, message) == True
    return message

def json_custom_parser(obj):
    """
        A custom json parser to handle json.dumps calls properly for Decimal and Datetime data types.
    """
    if isinstance(obj, Decimal):
        return '{0:f}'.format(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return time.mktime(obj.timetuple())
    else:
        raise TypeError(obj)