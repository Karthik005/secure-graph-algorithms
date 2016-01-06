#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 13:46:33

import abb_funcs as abb
import net_recv as nr
import net_share as ns
import sys 
from time import sleep 

# globals
N = 104059
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
	z_share = abb.compare(self_pid, party_conns, (x_share, y_share), t, N, nB, act_parties, 4)
	print "comparison done"
	ans = nr.reconstruct_secret(party_conns, z_share, self_pid, nB, N)
	print "x > y:", ans
	
if __name__ == '__main__':
	ip = []
	for i in open('addresses'):
		ip.append(i[:-1])
	act_parties = (int(sys.argv[3]), int(sys.argv[4]))
	# test_abb_rec_mult(sys.argv[1], int(sys.argv[2]), ip, 1)
	# test_abb_inequality(sys.argv[1], int(sys.argv[2]), ip, 1, act_parties)
	test_abb_equality(sys.argv[1], int(sys.argv[2]), ip, 1, act_parties)
