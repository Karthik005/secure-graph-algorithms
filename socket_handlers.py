#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: karthik
# @Date:   2016-01-02 19:30:21


import socket as sct


# globals
SIGLEN = 56
# --------------#

def mpc_connect(p_id, ip):
	'''
	connect to remaining socket_list
	@arg		: party ID, all party IPs
	@returns	: socket objects connected to other socket_list
	'''
	socket_list = []
	# Listen to requests from p_j where j < i
	for i in range(1, p_id):
		sock = sct.socket(sct.AF_INET, sct.SOCK_STREAM)
		sock.setsockopt(sct.SOL_SOCKET, sct.SO_REUSEADDR, 1)
		sock.bind((ip[i-1], 9000+(p_id*10 + (i-1))))
		sock.listen(2)
		conn, address = sock.accept()
		socket_list.append(conn)
		print "Connected to party", i

	# Wait for a byte from p_(i-1) to signal that all socket_list are waiting
	# for p_i's request to connect
	if p_id > 1:
		socket_list[-1].recv(1)

	# Fill in a null socket for p_i
	socket_list.append(None)

	sleep(1)

	# Send requests to other socket_list p_j, j > i
	for i in range(p_id+1, len(ip)+1):
		sock = sct.socket(sct.AF_INET, sct.SOCK_STREAM)
		sock.setsockopt(sct.SOL_SOCKET, sct.SO_REUSEADDR, 1)
		sock.connect((ip[i-1], 9000+(i*10 + p_id)))
		print "Connected to party", i
		socket_list.append(sock)

	# Signal to p_(i+1) that p_i's connection round is over
	if len(ip) > p_id:
		socket_list[p_id].send(' ')
		
	return socket_list



def recv_share(src_sock, nB):
	'''
	 Receive shares from the dealer
	  @arg		: source socket, no. of bytes to be received
	  @returns	: integer share
	'''
	share = src_sock.recv(nB)
	return int(share.encode('hex'), 16)


'''
 Receive all shares from other parties
  @arg		: list of parties, bytes per share
  @returns	: list of shares
'''
def recv_shares(parties, nB):
	sh = []
	party_id = 1
	for party in parties:
		sh.append((party_id, recv_share(party, nB)))
		party_id = party_id + 1
	return sh



def recv_sig(src_sock):
	'''
	receive signal messages
	'''
	sig = src_sock.recv(SIGLEN)
	return sig



def send_sig(src_sock, sig):
	'''
	send signal messages
	'''
	sig = src_sock.send(sig)
	return sig


def close_socks(socket_list):
	'''
	close all sockets
	@arg		: list of socket objects
	@returns 	: none
	'''
	for sock in socket_list:
		sock.close()
	return

