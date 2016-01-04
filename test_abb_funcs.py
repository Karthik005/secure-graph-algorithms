#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 13:46:33

import abb_funcs as abb
import net_recv as nr
import net_share as ns
import sys 

# globals
N = 104059
# --------

def test_abb_add(dealer_ip, self_pid, party_ips, t, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.add(self_pid, party_conns, [x_share, y_share], N)
	ans = nr.reconstruct_secret(party_conns, z_share[1], self_pid, nB, N)
	print ans

def test_abb_mult(dealer_ip, self_pid, party_ips, t, nB = 20):
	dealer_conn = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = (self_pid, nr.recv_share(dealer_conn, nB))
	y_share = (self_pid, nr.recv_share(dealer_conn, nB))
	z_share = abb.mult(self_pid, party_conns, (x_share, y_share), t, N, nB)
	ans = nr.reconstruct_secret(party_conns, z_share[1], self_pid, nB, N)
	print ans

if __name__ == '__main__':
	ip = []
	for i in open('addresses'):
		ip.append(i[:-1])
	test_abb_add(sys.argv[1], int(sys.argv[2]), ip, 1)
	test_abb_mult(sys.argv[1], int(sys.argv[2]), ip, 1)
