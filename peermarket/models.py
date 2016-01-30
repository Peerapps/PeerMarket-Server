from django.db import models

###RAW DATA FROM BLOCKCHAIN/external data stores###

class Transaction(models.Model):
    """
        Raw peermarkets data parsed from blockchain
    """
    tx_id = models.CharField(max_length=255, primary_key=True)
    block_number_created = models.IntegerField(default=0, blank=True, null=True)
    time_created = models.IntegerField(default=0, blank=True, null=True)
    peercoin_address = models.CharField(max_length=255, default="", blank=True, null=True)

    payload_retrieved = models.BooleanField(default=False)
    payload_executed = models.BooleanField(default=False)
    payload_action = models.CharField(max_length=255, default="", blank=True, null=True)
    
    pm_key = models.CharField(max_length=255, db_index=True, default="", blank=True, null=True)
    pm_payload = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.tx_id)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        app_label = "peermarket"

###PROCESSED DATA###

class Listing(models.Model):
    """
        Listings automatically disappear after 14 days.
        Only the quantity can be updated after a listing has been posted.
    """
    tx_id = models.CharField(max_length=255, primary_key=True)
    category = models.CharField(max_length=255, default="", blank=True, null=True)
    subcategory = models.CharField(max_length=255, default="", blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    requested_peercoin = models.CharField(max_length=255, default="", blank=True, null=True)
    peercoin_address = models.CharField(max_length=255, default="", blank=True, null=True)

    block_number_created = models.IntegerField(default=0, blank=True, null=True)
    time_created = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.tx_id)

    class Meta:
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        app_label = "peermarket"

class Offer(models.Model):
    tx_id = models.CharField(max_length=255, primary_key=True)
    listing_tx_id = models.CharField(max_length=255, default="", blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    offered_peercoin = models.CharField(max_length=255, default="", blank=True, null=True)
    peercoin_address = models.CharField(max_length=255, default="", blank=True, null=True)
    block_number_created = models.IntegerField(default=0, blank=True, null=True)
    time_created = models.IntegerField(default=0, blank=True, null=True)

    ### Offer Status
    # 1 = Open
    # 2 = Canceled by offerer
    # 3 = Rejected by lister
    # 4 = Accepted by lister
    offer_status = models.IntegerField(default=1, blank=True, null=True)

    #These will be null until offer status changes from Open
    tx_id_status_change = models.CharField(max_length=255, default="", blank=True, null=True)
    block_number_status_change = models.IntegerField(default=0, blank=True, null=True)
    time_status_change = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.tx_id)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        app_label = "peermarket"

class Message(models.Model):
    tx_id = models.CharField(max_length=255, primary_key=True)
    listing_tx_id = models.CharField(max_length=255, default="", blank=True, null=True)
    offer_tx_id = models.CharField(max_length=255, default="", blank=True, null=True)
    peercoin_address = models.CharField(max_length=255, default="", blank=True, null=True)

    message = models.TextField(blank=True, null=True)
    block_number_created = models.IntegerField(default=0, blank=True, null=True)
    time_created = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.tx_id)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        app_label = "peermarket"
