#!/bin/sh

set -e

# install certbot
command -v certbot > /dev/null || (
  apk update && apk add certbot certbot-nginx
)

# perform certificate install
grep -E "server_name _|localhost;" /etc/nginx/nginx.conf > /dev/null || (
  domain=$(grep server_name /etc/nginx/nginx.conf -m 1 | tr -s " " | sed "s/^ //" | tr -d ";" | cut -d " " -f 2)

  # shellcheck disable=SC2015
  certbot certificates -d "$domain" 2> /dev/null | grep "$domain" > /dev/null && (
    echo "SSL certificates already exist"
  ) || (
    echo "Creating SSL for $domain"
    certbot --nginx -d "$domain" --register-unsafely-without-email --agree-tos -n
  )
)