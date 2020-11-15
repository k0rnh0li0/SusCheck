#!/usr/bin/env python3

from scapy.all import *

INFO_HEADER = b'p\x85\xc2\xce'

# check whether the specified packet is the Info Packet
# that we're interested in
def check_header(pkt):
    if len(pkt) <= len(INFO_HEADER):
        return False

    for i in range(len(INFO_HEADER)):
        if pkt[i] != INFO_HEADER[i]:
            return False

    return True

# parse data from each player from the info packet
# returns a list of tuples (name, data), or None
def parse_info(pkt):
    plist = None
    players = []

    # scan for start of player list
    for pidx in range(len(pkt) - 4):
       if pkt[pidx] == 0x1e and pkt[pidx + 2] == 0 and pkt[pidx + 3] == 0:
           plist = pkt[pidx + 1:]
           break

       pidx = pidx + 1

    if plist is None:
        return None

    while len(plist) > 0:
        plist = plist[3:]
        pname = plist[1:plist[0] + 1].decode("ascii")
        plist = plist[plist[0] + 1:]
        pdata = plist[:2 * plist[5] + 6]

        players.append((pname, pdata))

        plist = plist[2 * plist[5] + 6:]

    return players

# takes a list of player tuples, and returns a list of impostor tuples
def get_impostors(players):
    return [x for x in players if x[1][4] == 0x02]

# returns a string containing player names separated by commas based
# on a player tuple list, for pretty-printing
def players_string(players):
    result = ""
    for i in range(len(players)):
        result = result + players[i][0]
        if i < len(players) - 1:
            result = result + ", "
    return result

def process_pkt(pkt):
    pkt = bytes(pkt)
    players = None
    if check_header(pkt):
        try:
            players = parse_info(pkt)
        except:
            # fail silently - a lot of packets will
            # not be what we want
            return

    if players is None:
        return

    impostors = get_impostors(players)

    if len(impostors) == 0:
        return
    elif len(impostors) == 1:
        print("IMPOSTOR: ", end='')
    else:
        print("IMPOSTORS: ", end='')

    print(players_string(impostors))

if __name__ == "__main__":
    sniff(filter="udp", prn=process_pkt)
