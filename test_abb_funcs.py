#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 13:46:33

import abb_funcs as abb
import net_recv as nr
import net_share as ns
import sys 
from time import sleep 
from math import log, ceil
from secure_bellman_ford import *

# globals
N = 104059
#N = 110566836484895734954398231583463152069845275179779537530039974333624866315077
#N = 314853400076558016540142136275780708481
#N = 13317897048299897509
#N = 4190502817
#N = 36209
# --------

def test_abb_add(dealer_ip, self_pid, party_ips, t, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.add(self_pid, party_conns, [x_share[1], y_share[1]], N)
	print x_share, y_share, z_share
	ans = nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)
	print "sum: ",ans

def test_abb_mult(dealer_ip, self_pid, party_ips, t, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.mult(self_pid, party_conns, (x_share, y_share), t, N, nB)
	print x_share, y_share, z_share
	ans = nr.reconstruct_secret(party_conns, (z_share[0],int(z_share[1])), self_pid, nB, N)
	print "product: ", ans


def test_abb_rec_mult(dealer_ip, self_pid, party_ips, t, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	a_share = (self_pid, nr.recv_share(dealer_conn, nB))
	b_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.rec_mult(self_pid, party_conns, [x_share, y_share, a_share, b_share], t, N, nB)
	ans = nr.reconstruct_secret(party_conns, (z_share[0],int(z_share[1])), self_pid, nB, N)
	print "product: ", ans


def test_abb_equality(dealer_ip, self_pid, party_ips, t, act_parties, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	for i in xrange(10):
		z_share = abb.test_equality(self_pid, party_conns, (x_share, y_share), t, N, nB, act_parties, 10)
		ans = nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)
		print "is equal: ", ans

def test_abb_inequality(dealer_ip, self_pid, party_ips, t, act_parties, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.compare(self_pid, party_conns, (x_share, y_share), t, N, nB, act_parties, 8)
	print "comparison done"
	ans = nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)
	print "x >= y:", ans

def test_abb_boolean(dealer_ip, self_pid, party_ips, t, act_parties, nB):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.is_boolean(self_pid, party_conns, x_share, t, N, nB, act_parties)
	print "First value: ", nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)
	z_share = abb.is_boolean(self_pid, party_conns, y_share, t, N, nB, act_parties)
	print "Second value: ", nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)

def test_bf(dealer_ip, pid, party_ip, s, N, t, nB):
	dealer = nr.connect_to_dealer(dealer_ip, pid)
	parties = nr.connect_to_parties(pid, party_ip)
	G = nr.recv_graph(dealer, nB)
	print nr.reconstruct_graph(parties, G, pid, nB, N)
	s_ind = [0 for i in range(0, len(G))]
	s_ind[s] = 1
	p_sh, d_sh, err_sh = secure_bellman_ford(pid, parties, G, s_ind, 1, N, t, True)
	p, d, err = reconstruct_preds_dists(pid, parties, p_sh, d_sh, err_sh, N)
	print p, d, err
	
	
if __name__ == '__main__':
	ip = []
	for i in open('addresses'):
		ip.append(i[:-1])
	#act_parties = (int(sys.argv[3]), int(sys.argv[4]))
	nB = int(ceil(log(N) / (log(2)*8)))
	#while 1:
	test_bf(sys.argv[1], int(sys.argv[2]), ip, 0, N, 1, nB)
	#test_abb_boolean(sys.argv[1], int(sys.argv[2]), ip, 1, act_parties, nB)
		#test_abb_inequality(sys.argv[1], int(sys.argv[2]), ip, 1, act_parties, nB)
		#test_abb_equality(sys.argv[1], int(sys.argv[2]), ip, 1, act_parties, nB)
		# test_abb_rec_mult(sys.argv[1], int(sys.argv[2]), ip, 1)
		#test_abb_mult(sys.argv[1], int(sys.argv[2]), ip, 1, nB)
