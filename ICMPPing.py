#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii  


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages


def checksum(string): 
    csum = 0
    countTo = (len(string) // 2) * 2  
    count = 0

    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal 
        csum = csum & 0xffffffff  
        count = count + 2
    
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff 
    
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum 
    answer = answer & 0xffff 
    answer = answer >> 8 | (answer << 8 & 0xff00)

    answer = socket.htons(answer)

    return answer
    
def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):

    timeLeft = timeout

    timeStart = time.time()
    ready = select.select([icmpSocket], [], [], timeout)

    if ready[0] == []:
        return # Timeout

    timeAfter = time.time() - timeStart

    timeRecieved = time.time() * 1000

    recvPacket, address = icmpSocket.recvfrom(1024)
    header = recvPacket[20:28]
    type, code, chkSum, packetID, sequence = struct.unpack("bbHHh", header)

    timeLeft = timeLeft - timeAfter

    # Gets the ping request
    if type != ICMP_ECHO_REQUEST and packetID == ID:
        return (timeRecieved, timeLeft)

    if timeLeft <= 0:
        return
    
def sendOnePing(icmpSocket, destinationAddress, ID):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, ID, 1)

    chkSum = checksum(header)

    packet = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, chkSum, ID, 1)

    icmpSocket.sendto(packet, (destinationAddress, 0))

    return time.time() * 1000
    
def doOnePing(destinationAddress, timeout): 
    icmp = socket.getprotobyname("ICMP")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    ID = os.getpid() & 0xFFFF

    timeSent = sendOnePing(s, destinationAddress, ID)
    timeRecieved = receiveOnePing(s, destinationAddress, ID, timeout)

    s.close()
    return (timeRecieved[0] - timeSent, timeRecieved[1])

def ping(host, timeout=1):
    try:
        ip = socket.gethostbyname(host)
    except:
        print("IP not found for address: "+host)
        return

    for x in range(0, 3):
        delay = doOnePing(ip,timeout)
        print("Pining "+host + " ["+ip+"]: time="+str(round(delay[0]))+"ms TTL="+str(round(delay[1])))
        time.sleep(1)
    

ping("lancaster.ac.uk", 5)
ping("files.anifox.moe", 5)
ping("google.co.uk", 5)
ping("stasfasdas.com",2)

