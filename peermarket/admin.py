from django.contrib import admin

#from models import Blog
#class BlogAdmin(admin.ModelAdmin):
#    list_display = ('key', 'address_from', 'block_index', 'tx_id')
#    search_fields = ('key', 'address_from', 'block_index', 'tx_id')
#admin.site.register(Blog, BlogAdmin)

from models import Transaction
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_id', 'peercoin_address', 'payload_retrieved', 'payload_executed', 'pm_key', 'pm_payload')
    search_fields = ('tx_id', 'peercoin_address', 'payload_retrieved', 'payload_executed', 'pm_key', 'pm_payload')
admin.site.register(Transaction, TransactionAdmin)

from models import Listing
class ListingAdmin(admin.ModelAdmin):
    list_display = ('tx_id', 'category', 'subcategory', 'quantity', 'requested_peercoin', 'peercoin_address')
    search_fields = ('tx_id', 'category', 'subcategory', 'peercoin_address')
admin.site.register(Listing, ListingAdmin)

from models import Message
class MessageAdmin(admin.ModelAdmin):
    list_display = ('tx_id', 'listing_tx_id', 'offer_tx_id', 'peercoin_address', 'message')
    search_fields = ('tx_id', 'listing_tx_id', 'offer_tx_id', 'peercoin_address')
admin.site.register(Message, MessageAdmin)


from models import Offer
class OfferAdmin(admin.ModelAdmin):
    list_display = ('tx_id', 'listing_tx_id', 'quantity', 'offered_peercoin', 'peercoin_address', 'offer_status', 'tx_id_status_change')
    search_fields = ('tx_id', 'listing_tx_id', 'peercoin_address', 'offer_status', 'tx_id_status_change')
admin.site.register(Offer, OfferAdmin)
