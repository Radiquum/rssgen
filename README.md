# Python RSS feed generator

supported services:

+ Yandex Music ['/new-releases']

## requirements

1. docker
2. docker-compose

## how to run?

1. clone this repo
2. (optional) export cookies.txt file for site 'yandex.ru' from your browser, and place it to uploads/cookies-yandexmusic-[your username].txt
3. run `docker build -t=rssgen .`
4. run `docker-compose up -d`

alternatively you can just install requirements.txt and run app.py as python script, but you **MUST** install firefox on your system!
also you'll **need** to modify modules/[service].py, to enable it for local web-browser!

your app will be available on `http://[ip]:5000/`

## how to use?

1. generate feed
   + for Yandex Music
     1. `http://[ip]:5000/api/yandex-music/new-releases/feed-update`
     2. (optional) you can add parameter `username=[username from cookies file]` to fetch your new releases
     3. (optional) you can add parameter `fetch=[0-100]` to fetch this number of albums (default: 50)

2. get your generated feed
   + for Yandex Music
     1. you can access it by `http://[ip]:5000/yandex-music/new-releases`
     2. (optional) you can add parameter `username=[username from cookies file]` to fetch your new releases
