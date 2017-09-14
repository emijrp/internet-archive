
curl -d "" "https://www.wikidata.org/wiki/Special:SiteMatrix" 2> /dev/null | grep -ioE '//[^"]+">' | sort | uniq | cut -d'/' -f3 | cut -d'/' -f1 | cut -d'"' -f1 | awk '$0="https://"$0""' > wikimedia-urls.txt
python3 archive-urls.py wikimedia-urls.txt force
