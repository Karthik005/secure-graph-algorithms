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
 Helper function to convert int to a string of `n' bytes
  @arg		: input integer, n bytes
  @returns	: output string of bytes
'''
def int_to_bytes(x, n):
	b = bytearray()
	bytes_added = 0
	x = int(x)
	while x > 0:
		b.append(x%256)
		x = x >> 8
		bytes_added = bytes_added + 1
	while bytes_added < n:
		b.append(0)
		bytes_added = bytes_added + 1
	return str(b)[::-1]

'''
 Function to distribute shares of a secret to the respective parties
  @arg		: shares, sockets of parties
  @returns	: nothing
'''
def distribute_secret(sh, parties, no_of_bytes):
	if len(sh) != len(parties):
		print "Shares != parties", sh, parties
		sys.exit()
	for i in range(0, len(sh)):
		# Party P_i gets f(i+1); assume that every party is listening
		# for the graph element
		parties[i].send(int_to_bytes(sh[i][1], no_of_bytes))

'''
 Function to share the entire adjacency matrix
  @arg		: graph, parties, N
  @returns	: nothing
'''
def share_graph(G):
	t = 1
	N = 104059
	# Create sockets
	parties = connection_phase()
	for row in G:
		for val in row:
			# Create list of shares for this value
			sh = gen_shares(3, t, val, N)
			# Send these shares to the parties
			#NOTE: change no. of bytes, corresponding to N
			distribute_secret(sh, parties, 20)

if __name__ == '__main__':
	# Read the adjacency matrix from the graph file
	G = [[int(val) for val in line.split()] for line in open('graph')]
	share_graph(G)
