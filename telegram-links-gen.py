
import sys

def main():
    channel = sys.argv[1]
    num = int(sys.argv[2])
    print('https://t.me/%s' % (channel))
    print('https://t.me/%s/' % (channel))
    print('https://t.me/s/%s/' % (channel))
    print('https://t.me/s/%s' % (channel))
    for x in range(0, num+1):
        print('https://t.me/%s/%s' % (channel, x))
        print('https://t.me/s/%s/%s' % (channel, x))

if __name__ == '__main__':
    main()
