#!/bin/sh

set -e

# install certbot
command -v certbot > /dev/null || (
  apk update && apk add certbot certbot-nginx
)

# perform certificate install
grep -E "server_name _|localhost;" /etc/nginx/nginx.conf > /dev/null || (
  domain=$(grep server_name /etc/nginx/nginx.conf | tr -s " " | sed "s/^ //" | tr -d ";" | cut -d " " -f 2)

  # shellcheck disable=SC2015
  certbot certificates -d "$domain" | grep "$domain" > /dev/null 2> /dev/null && (
    echo "SSL certificates already exist"
    exit 0
  )

  echo "Creating SSL for $domain"
  certbot --nginx -d "$domain" --register-unsafely-without-email --agree-tos -n
)