#!/usr/bin/env python3

# This script detects the identities of impostors in
# Among Us and outputs them for the user.
# To use it, simply leave the script running while you
# join games. At the start of each game, the script
# will notify you who the impostor(s) are.
#
# Please note that many assumptions and guesses were
# made while writing this. My conception of the packet
# structure may not be fully accurate. As a result,
# the script does not detect impostors 100% of the time.
# It's more like 90-95%. There is room for improvement.
#
# Requires scapy:
# python -m pip install scapy
#
# This program is Free Software, licensed under
# GPLv3. For more information, see LICENSE.txt.

import scapy.all

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

    # parse name and data from each player until
    # we have exhausted the list
    while len(plist) > 0:
        plist = plist[3:]
        pname = plist[1:plist[0] + 1].decode("ascii")
        plist = plist[plist[0] + 1:]
        pdata = plist[:2 * plist[5] + 6]

        players.append((pname, pdata))

        plist = plist[2 * plist[5] + 6:]

    return players

# takes a list of player tuples, and returns a list
# with all the non-impostor players removed
def get_impostors(players):
    return [x for x in players if x[1][4] == 0x02]

# returns a comma-separated string of player names based
# on a player tuple list
def players_string(players):
    result = ""
    for i in range(len(players)):
        result = result + players[i][0]
        if i < len(players) - 1:
            result = result + ", "
    return result

# main packet handling function
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
    print("\n  ==============================")
    print("  ==                          ==")
    print("  == I AM THE GREAT KORNHOLIO ==")
    print("  ==  ARE U THREATENING ME??  ==")
    print("  ==                          ==")
    print("  ==         SusCheck         ==")
    print("  ==    Impostor  Detector    ==")
    print("  ==                          ==")
    print("  ==============================\n")

    print("Scanning for impostors...")
    print("(CTRL+C to exit)")

    scapy.all.sniff(filter="udp", prn=process_pkt)
