from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^submit_transactions/$', "peermarket.views.submit_transactions"), #includes transactions and payloads
    url(r'^get_transaction/$', "peermarket.views.get_transaction"), #For a given transaction ID, return it's payload
    url(r'^get_listings/$', "peermarket.views.get_listings"), #allows filtering, flag to include offers
    url(r'^get_blockchain_data/$', "peermarket.views.get_blockchain_data"), #From another server, get raw signed data per block
)