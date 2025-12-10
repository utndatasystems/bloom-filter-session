# bloom-filter-session
Interactice game for the teaching session on "Bloom filter" 


## Server Setting

### Python Enviroment

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### SSL setting

Get the free domain on [noip](https://www.noip.com/). \
Get the SSL certificate with [Let's Encrypt](https://letsencrypt.org/).

```
DOMAIN=bloom-filter.ddns.net
sudo apt update
sudo apt install certbot
sudo certbot certonly --standalone -d $DOMAIN
# after this you will get the cert and key

# 1) Make a private certs dir for your app
sudo mkdir -p /home/ubuntu/bloom-filter-session/certs
sudo chown ubuntu:ubuntu /home/ubuntu/bloom-filter-session/certs
sudo chmod 700 /home/ubuntu/bloom-filter-session/certs

# 2) Copy the cert + key (adjust domain if different)
SRC=/etc/letsencrypt/live/$DOMAIN
DST=/home/ubuntu/bloom-filter-session/certs

sudo install -m 600 -o ubuntu -g ubuntu "$SRC/fullchain.pem" "$DST/fullchain.pem"
sudo install -m 600 -o ubuntu -g ubuntu "$SRC/privkey.pem"   "$DST/privkey.pem"
```

## Run the API

```
python python/bloom.py
```