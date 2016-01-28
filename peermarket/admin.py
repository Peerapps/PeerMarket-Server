from django.contrib import admin

#from models import Blog
#class BlogAdmin(admin.ModelAdmin):
#    list_display = ('key', 'address_from', 'block_index', 'tx_id')
#    search_fields = ('key', 'address_from', 'block_index', 'tx_id')
#admin.site.register(Blog, BlogAdmin)

from models import Transaction
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_id', 'peercoin_address', 'payload_retrieved', 'pm_key', 'pm_payload')
    search_fields = ('tx_id', 'peercoin_address', 'payload_retrieved', 'pm_key', 'pm_payload')
admin.site.register(Transaction, TransactionAdmin)