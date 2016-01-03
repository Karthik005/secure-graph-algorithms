'''
 This file contains code to emulate the receivers of the shares
'''

import sys, socket
from shamir_sharing import *
from time import sleep

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
 Function to set up servers to listen to parties with ID < p_id, and sockets
 connected to parties with ID > p_id
  @arg		: party ID, all party IPs
  @returns	: socket objects connected to other parties
'''
def connect_to_parties(p_id, ip):
	parties = []
	# Listen to requests from p_j where j < i
	for i in range(0, p_id-1):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((ip[i], 9000+(p_id*10 + (i+1))))
		sock.listen(2)
		conn, address = sock.accept()
		parties.append(conn)
		print "Connected to party", (i+1)

	# Wait for a byte from p_(i-1) to signal that all parties are waiting
	# for p_i's request to connect
	if p_id > 1:
		parties[-1].recv(1)

	# Fill in a null socket for p_i
	parties.append(None)

	sleep(1)

	# Send requests to other parties p_j, j > i
	for i in range(p_id, len(ip)):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((ip[i], 9000+((i+1)*10 + p_id)))
		print "Connected to party", (i+1)
		parties.append(sock)

	# Signal to p_(i+1) that p_i's connection round is over
	if len(ip) > p_id:
		parties[p_id].send(' ')
		
	return parties

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

	print 'Attempting to connect to other parties'
	ip = []
	for i in open('addresses'):
		ip.append(i[:-1])
	parties = connect_to_parties(p_id, ip)
	print parties
