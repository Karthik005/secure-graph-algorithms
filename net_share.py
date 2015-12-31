'''
 This file is to test the distribution of shamir shares over the network
 The ID of this party is passed as a command line argument
 Party P_i communicates with P_j on its own port 8000+j
 
'''

import sys, socket
from shamir_sharing import *

'''
 Function to read IP addresses from stdin and return a list of bound sockets
 corresponding to them
  @arg		: none
  @returns	: list of sockets
'''
def connection_phase():
	parties = []
	party_id = 0
	# Get list of IP addresses, create sockets to bind
	for ip in open('addresses'):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		'''
		try:
			sock.bind((ip, 8000 + party_id))
		except socket.error as msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()
		print 'Socket bound for party ' + str(party_id)
		'''
		party_id = party_id + 1
		sock.connect((ip[:-1], 8000+party_id))
		parties.append(sock)
	return parties

#def send_secret_shares(sh, parties, own_id):
#	for i in range(1, own_id):
'''
 Helper function to convert int to a string of bytes
  @arg		: input integer
  @returns	: output string of bytes
'''
def int_to_bytes(x):
	b = bytearray()
	while x > 0:
		b.append(x%256)
		x = x >> 8
	return str(b)[::-1]

'''
 Function to distribute shares of a secret to the respective parties
  @arg		: shares, sockets of parties
  @returns	: nothing
'''
def distribute_secret(sh, parties):
	if len(sh) != len(parties):
		print "Shares != parties", sh, parties
		sys.exit()
	for i in range(0, len(sh)):
		# Party P_i gets f(i+1); assume that every party is listening
		# for the graph element
		parties[i].send(int_to_bytes(sh[i][1]))

'''
 Function to share the entire adjacency matrix
  @arg		: graph, parties, N
  @returns	: nothing
'''
def share_graph(G):
	t = 3
	N = 104059
	# Create sockets
	parties = connection_phase()
	for row in G:
		for val in row:
		# Create list of shares for this value
		sh = gen_shares(6, t, val, N)
		# Send these shares to the parties
		distribute_secret(sh, parties)


# Read the adjacency matrix from the graph file
G = [[int(val) for val in line.split()] for line in open('graph')]

