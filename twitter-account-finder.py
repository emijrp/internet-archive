
import os
import pickle
import re
import time
import urllib.request

def loadTwitterAccounts():
    accounts = {}
    if os.path.exists('twitter-accounts.pickle'):
        with open('twitter-accounts.pickle', 'rb') as f:
            accounts = pickle.load(f)
    return accounts.copy()

def saveTwitterAccounts(accounts={}):
    with open('twitter-accounts.pickle', 'wb') as f:
        pickle.dump(accounts, f)

def main():
    seeds = ['BNE_biblioteca']
    done = []
    accounts = loadTwitterAccounts()
    for k, v in accounts.items():
        if v:
            done.append(k)
        else:
            seeds.append(k)
    print('Loaded %d accounts. Seeds: %d, Done: %d' % (len(accounts.keys()), len(seeds), len(done)))
    while seeds:
        for seed in seeds:
            if seed in done:
                seeds.remove(seed)
                continue
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"
            req = urllib.request.Request('https://twitter.com/%s' % (seed), headers = headers)
            
            try:
                html = str(urllib.request.urlopen(req).read())
            except:
                time.sleep(10)
                try:
                    html = str(urllib.request.urlopen(req).read())
                except:
                    time.sleep(60)
                    html = str(urllib.request.urlopen(req).read())
            
            try: #error in html
                screennames = re.findall(r'(?im)data-screen-name="([^" ]+?)"', html)
                screennames = list(set(screennames))
                name = re.findall(r'(?im),&quot;name&quot;:&quot;(.*?)&quot;,', html)[0]
                tweets = int(re.findall(r'statuses_count&quot;:(\d+),', html)[0])
                followers = int(re.findall(r'followers_count&quot;:(\d+),', html)[0])
                following = int(re.findall(r'friends_count&quot;:(\d+),', html)[0])
                favorites = int(re.findall(r'favourites_count&quot;:(\d+),', html)[0])
            except:
                continue
            
            accounts[seed] = { 'name': name, 'tweets': tweets, 'followers': followers, 'following': following, 'favorites': favorites}
            print(seed, 'https://twitter.com/%s' % seed, accounts[seed])
            for screenname in screennames:
                if screenname in seed or screenname in done:
                    continue
                if screenname not in accounts:
                    accounts[screenname] = {}
                    if not screenname in seeds:
                        seeds.append(screenname)
            print('Seeds:', len(seeds), 'Done:', len(done))
            done.append(seed)
            if len(done) % 100 == 0:
                saveTwitterAccounts(accounts=accounts)
        seeds = list(set(seeds))

if __name__ == "__main__":
    main()
