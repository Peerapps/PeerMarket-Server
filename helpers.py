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
from peermarket.errors import BadPeermarketTransaction

import shutil

def process_pm_query(transaction, pm_query):
    if 'action' not in pm_query:
        raise BadPeermarketTransaction('Unable to detect action requested in: '+str(pm_query))

    if pm_query['action'] == 'new_listing':
        listing_details = {
            "tx_id": transaction.tx_id,
            "category": pm_query['category'],
            "subcategory": pm_query['subcategory'],
            "quantity": pm_query['quantity'],
            "requested_peercoin": pm_query['requested_peercoin'],
            "peercoin_address": transaction.peercoin_address,
            "block_number_created": transaction.block_number_created,
            "time_created": transaction.time_created
        }
        new_listing = Listing(**listing_details)
        new_listing.save()

        if pm_query.get('message', ''):
            message_details = {
                "tx_id": transaction.tx_id,
                "listing_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": pm_query['message']
            }
            new_message = Message(**message_details)
            new_message.save()

    elif pm_query['action'] == 'update_listing':

        try:
            existing_listing = Listing.objects.get(tx_id=pm_query['listing_tx_id'], peercoin_address=transaction.peercoin_address)
        except Listing.DoesNotExist:
            raise BadPeermarketTransaction('Update Listing Error: No listing found with tx_id='+str(pm_query['listing_tx_id'])+" and peercoin_address="+str(transaction.peercoin_address))
        summary_of_changes = ""

        if 'quantity' in pm_query:
            summary_of_changes += "Updated quantity from " + str(existing_listing.quantity) + " to " + str(pm_query['quantity']) + ".\n"
            existing_listing.quantity = pm_query['quantity']
        if 'category' in pm_query:
            summary_of_changes += "Updated category from " + str(existing_listing.category) + " to " + str(pm_query['category']) + ".\n"
            existing_listing.category = pm_query['category']
        if 'subcategory' in pm_query:
            summary_of_changes += "Updated subcategory from " + str(existing_listing.category) + " to " + str(pm_query['subcategory']) + ".\n"
            existing_listing.subcategory = pm_query['subcategory']
        if 'requested_peercoin' in pm_query:
            summary_of_changes += "Updated requested_peercoin from " + str(existing_listing.requested_peercoin) + " to " + str(pm_query['requested_peercoin']) + ".\n"
            existing_listing.requested_peercoin = pm_query['requested_peercoin']

        existing_listing.save()

        message = ""
        if pm_query.get('message', ''):
            message = pm_query['message']
            if summary_of_changes:
                message = message + "\n\n----------\n\n" + summary_of_changes
        else:
            message = summary_of_changes

        if message:
            message_details = {
                "tx_id": transaction.tx_id,
                "listing_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": message
            }
            new_message = Message(**message_details)
            new_message.save()

    elif pm_query['action'] == 'new_offer':
        offer_details = {
            "tx_id": transaction.tx_id,
            "listing_tx_id": pm_query['listing_tx_id'],
            "quantity": pm_query['quantity'],
            "offered_peercoin": pm_query['offered_peercoin'],
            "peercoin_address": transaction.peercoin_address,
            "block_number_created": transaction.block_number_created,
            "time_created": transaction.time_created
        }
        offer_details = Offer(**offer_details)
        offer_details.save()

        if pm_query.get('message', ''):
            message_details = {
                "tx_id": transaction.tx_id,
                "offer_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": pm_query['message']
            }
            new_message = Message(**message_details)
            new_message.save()

    elif pm_query['action'] == 'update_offer':

        try:
            existing_offer = Offer.objects.get(tx_id=pm_query['offer_tx_id'], peercoin_address=transaction.peercoin_address)
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Update Offer Error: No offer found with tx_id='+str(pm_query['offer_tx_id'])+" and peercoin_address="+str(transaction.peercoin_address))

        summary_of_changes = ""

        if 'quantity' in pm_query:
            summary_of_changes += "Updated quantity from " + str(existing_offer.quantity) + " to " + str(pm_query['quantity']) + ".\n"
            existing_offer.quantity = pm_query['quantity']
        if 'offered_peercoin' in pm_query:
            summary_of_changes += "Updated offered_peercoin from " + str(existing_offer.offered_peercoin) + " to " + str(pm_query['offered_peercoin']) + ".\n"
            existing_offer.offered_peercoin = pm_query['offered_peercoin']

        existing_offer.save()

        message = ""
        if pm_query.get('message', ''):
            message = pm_query['message']
            if summary_of_changes:
                message = message + "\n\n----------\n\n" + summary_of_changes
        else:
            message = summary_of_changes

        if message:
            message_details = {
                "tx_id": transaction.tx_id,
                "offer_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": message
            }
            new_message = Message(**message_details)
            new_message.save()

    elif pm_query['action'] == 'cancel_offer':

        try:
            existing_offer = Offer.objects.get(tx_id=pm_query['offer_tx_id'], peercoin_address=transaction.peercoin_address)
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Cancel Offer Error: No offer found with tx_id='+str(pm_query['offer_tx_id'])+" and peercoin_address="+str(transaction.peercoin_address))

        existing_offer.offer_status = 2 #Canceled by offerer
        existing_offer.tx_id_status_change = transaction.tx_id
        existing_offer.block_number_status_change = transaction.block_number_created
        existing_offer.time_status_change = transaction.time_created
        existing_offer.save()

    elif pm_query['action'] == 'reject_offer':

        try:
            existing_offer = Offer.objects.get(tx_id=pm_query['offer_tx_id'])
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Reject Offer Error: No offer found with tx_id='+str(pm_query['offer_tx_id']))

        #Only allow poster of listing to do this action
        try:
            existing_listing = Listing.objects.get(tx_id=existing_offer.listing_tx_id, peercoin_address=transaction.peercoin_address)
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Reject Offer Error: No listing found with tx_id='+str(existing_offer.listing_tx_id)+" and peercoin_address="+str(transaction.peercoin_address))

        existing_offer.offer_status = 3 #Rejected by lister
        existing_offer.tx_id_status_change = transaction.tx_id
        existing_offer.block_number_status_change = transaction.block_number_created
        existing_offer.time_status_change = transaction.time_created
        existing_offer.save()

        if pm_query.get('message', False):
            message_details = {
                "tx_id": transaction.tx_id,
                "offer_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": pm_query['message']
            }
            new_message = Message(**message_details)
            new_message.save()

    elif pm_query['action'] == 'accept_offer':

        try:
            existing_offer = Offer.objects.get(tx_id=pm_query['offer_tx_id'])
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Reject Offer Error: No offer found with tx_id='+str(pm_query['offer_tx_id']))

        #Only allow poster of listing to do this action
        try:
            existing_listing = Listing.objects.get(tx_id=existing_offer.listing_tx_id, peercoin_address=transaction.peercoin_address)
        except Offer.DoesNotExist:
            raise BadPeermarketTransaction('Reject Offer Error: No listing found with tx_id='+str(existing_offer.listing_tx_id)+" and peercoin_address="+str(transaction.peercoin_address))

        existing_offer.offer_status = 4 #Accepted by lister
        existing_offer.tx_id_status_change = transaction.tx_id
        existing_offer.block_number_status_change = transaction.block_number_created
        existing_offer.time_status_change = transaction.time_created
        existing_offer.save()

        if pm_query.get('message', False):
            message_details = {
                "tx_id": transaction.tx_id,
                "offer_tx_id": transaction.tx_id,
                "peercoin_address": transaction.peercoin_address,
                "block_number_created": transaction.block_number_created,
                "time_created": transaction.time_created,
                "message": pm_query['message']
            }
            new_message = Message(**message_details)
            new_message.save()

    else:
        raise BadPeermarketTransaction('Unable to parse pm_query requested in: '+str(pm_query))

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

    pm_queries = []
    transaction_payloads_executed = []
    for transaction in Transaction.objects.filter(payload_executed=False).order_by('-time_created'):
        try:
            for p in json.loads(transaction.pm_payload):
                pm_queries.append({'query': p, 'transaction':transaction})
        except:
            print 'Unable to process json string from payload: '+str(payload_str)
            #raise BadPeermarketTransaction('Unable to process json string from payload: '+str(payload_str))

        transaction_payloads_executed.append(transaction.tx_id)

    #Process New Listings First
    for pm_query_data in pm_queries:
        if pm_query_data['query']['action'] == 'new_listing':
            try:
                process_pm_query(pm_query_data['transaction'], pm_query_data['query'])
            except BadPeermarketTransaction as e:
                print e.message

    #Process New Offers Second
    for pm_query_data in pm_queries:
        if pm_query_data['query']['action'] == 'new_offer':
            try:
                process_pm_query(pm_query_data['transaction'], pm_query_data['query'])
            except BadPeermarketTransaction as e:
                print e.message

    #Process New Offers Second
    for pm_query_data in pm_queries:
        if pm_query_data['query']['action'] not in ['new_listing', 'new_offer']:
            try:
                process_pm_query(pm_query_data['transaction'], pm_query_data['query'])
            except BadPeermarketTransaction as e:
                print e.message

    Transaction.objects.filter(tx_id__in=transaction_payloads_executed).update(payload_executed=True)

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