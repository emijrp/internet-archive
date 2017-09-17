echo "https://dumps.wikimedia.org" > wikimedia-dumps-urls.txt
echo "https://dumps.wikimedia.org/backup-index.html" >> wikimedia-dumps-urls.txt
echo "https://dumps.wikimedia.org/mirrors.html" >> wikimedia-dumps-urls.txt
python3 archive.py wikimedia-dumps-urls.txt force

curl -A "Mozilla 5.0" "https://dumps.wikimedia.org/backup-index.html" 2> /dev/null | grep -ioE "[^/\"]+wiki/[0-9]+" | sort | uniq | awk '{split($0,a,"/"); print "https://dumps.wikimedia.org/"a[1]"/"a[2]"/"}' > wikimedia-dumps-urls.txt
python3 archive.py wikimedia-dumps-urls.txt force

curl -A "Mozilla 5.0" "https://dumps.wikimedia.org/backup-index.html" 2> /dev/null | grep -ioE "[^/\"]+wiki/[0-9]+" | sort | uniq | awk '{split($0,a,"/"); print "https://dumps.wikimedia.org/"a[1]"/"a[2]"/"a[1]"-"a[2]"-md5sums.txt\n""https://dumps.wikimedia.org/"a[1]"/"a[2]"/"a[1]"-"a[2]"-sha1sums.txt"}' > wikimedia-dumps-urls.txt
python3 archive.py wikimedia-dumps-urls.txt
