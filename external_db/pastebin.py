import requests
from __init__ import get_random_useragent

###############
#PASTEBIN
###############

def get_data(key):
    headers = {
        'User-Agent': get_random_useragent()
    }
    url = "http://pastebin.com/raw/"+key
    print "hitting ", url
    r = requests.get(url, headers=headers)
    if "Pastebin.com Unknown Paste ID" in r.text:
        print "Unable to pull from pastebin."
        return None
    elif "Error with this ID" in r.text:
        print "Unable to pull from pastebin."
        return None
    print "Pulled from pastebin"
    return r.text

def post_data(value):
    headers = {
        'User-Agent': get_random_useragent()
    }
    with requests.session() as c:
        t = c.get('http://pastebin.com/', headers=headers)

        try:
            csrf_token_post = t.text.split('name="csrf_token_post"')[1].split("hidden")[0].split('value="')[1].split('"')[0]
        except:
            csrf_token_post = ""
            print "Pastebin csrf_token_post not found!"

        r = c.post('http://pastebin.com/post.php', data={
            'paste_name': "",
            'paste_private': 1,
            'paste_expire_date': "N",
            "paste_format": 1,
            "paste_code": value,
            "submit_hidden": "submit_hidden",
            "csrf_token_post": csrf_token_post
        }, headers=headers)
        try:
            key = r.text.split("/raw/")[1].split('"')[0].lower()
            print "CREATED http://pastebin.com/raw/" + key
            return key.encode("hex")
        except:
            #Woah, you have reached your paste limit of 10 pastes per 24 hours. [IP-based].
            return None