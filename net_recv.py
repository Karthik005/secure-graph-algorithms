'''
 This file contains code to emulate the receivers of the shares
'''

import sys, socket
from shamir_sharing import *

'''
 Function to connect to the dealer on port = p_id
  @arg		: dealer IP, party ID
  @returns	: socket object set to listen
'''
def connect_to_dealer(dealer_ip, p_id):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((dealer_ip, 8000+p_id))
	sock.listen(2)
	d, address = sock.accept()
	return d

'''
 Receive shares from the dealer
  @arg		: dealer socket, no. of bytes to be received
  @returns	: integer share
'''
def recv_share(dealer, nB):
	share = dealer.recv(nB)
	return int(share.encode('hex'), 16)

'''
 Receive a graph of specific dimensions from the dealer
  @arg		: dealer socket, rows, columns, no of bytes
  @returns	: secret share of graph
'''
def recv_graph(dealer, rows, columns, nB):
	G = []
	for m in range(0, rows):
		row = []
		for n in range(0, columns):
			G_mn = recv_share(dealer, nB)
			row.append(G_mn)
		G.append(row)
	return G

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Arguments reqd.: <dealer IP> <P_id> <r> <c>"
	d_ip = sys.argv[1]
	p_id = int(sys.argv[2])
	r = int(sys.argv[3])
	c = int(sys.argv[4])
	nB = 20
	
	dealer = connect_to_dealer(d_ip, p_id)
	G = recv_graph(dealer, r, c, nB)

	for m in G:
		for n in m:
			print n,
		print ' '
