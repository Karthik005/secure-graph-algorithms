'''
 This file contains code to emulate the receivers of the shares
'''

import sys, socket
from shamir_sharing import *
from net_share import int_to_bytes
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

	class null_socket:
		def recv(self, a):
			return ' '
		def send(self, a):
			return None

	# Fill in a null socket for p_i
	parties.append(null_socket())

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
def recv_share(party, nB):
	share = party.recv(nB)
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

'''
 Send share to other parties
  @arg		: list of parties, share, no of bytes
  @returns	: list of shares
'''
def send_share(parties, share, nB):
	for party in parties:
		party.send(int_to_bytes(share, nB))



def reconstruct_secret(parties, self_share, self_pid, nB, N):
	'''
	reconstruct the secret by interpolation
	@arg		: list of parties, share, pid, number of bytes, N
	@returns	: list of shares
	'''
	send_share(parties, self_share[1], nB)
	recvd_shares = recv_shares(parties, nB)
	recvd_shares[self_pid-1] = self_share
	print "received shares: ", recvd_shares
	f = interpolate_poly(recvd_shares, N)
	return f(0)




'''
 Reconstruct graph of specific length by combining shares
  @arg		: list of parties, own shares of graph, party ID,
  		  bytes per share, N
  @returns	: adjacency matrix
'''
def reconstruct_graph(parties, G_sh, p_id, nB, N):
	# Send all shares to all parties
	for row in G_sh:
		for val in row:
			send_share(parties, val, nB)
	# Receive all shares from other parties
	G = []
	rows, columns = len(G_sh), len(G_sh[0])
	for i in range(0, rows):
		row = []
		for j in range(0, columns):
			sh = recv_shares(parties, nB)
			sh[p_id-1] = (p_id, G_sh[i][j])
			f = interpolate_poly(sh, N)
			row.append(f(0))
		G.append(row)
	return G


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
	G_sh = recv_graph(dealer, r, c, nB)

	print 'private shares:'
	for m in G_sh:
		for n in m:
			print n,
		print ' '

	print 'Attempting to connect to other parties'
	ip = []
	for i in open('addresses'):
		ip.append(i[:-1])
	parties = connect_to_parties(p_id, ip)
	#print parties

	print 'Reconstruct graph ovver the network'
	N = 104059
	G = reconstruct_graph(parties, G_sh, p_id, nB, N)

	for m in G:
		for n in m:
			print n,
		print ' '
