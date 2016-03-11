#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik and Yashvanth
# @Date:   2016-01-06 14:40:20

# Diagnostic print statements are commented out

import abb_funcs as abb
import net_recv as nr
import net_share as ns
import shamir_sharing as ss


# globals
nB = 20
# -------

def update_element(self_pid, socket_list, l, i, x, t, N):
	'''
	update shared list at shared position with shared value
	@arg		: self party id, list of party sockets, shared list, shared index list, share of val
	@return 	: shared list with element updated
	'''
	for j in xrange(len(l)):
		inter = abb.add(self_pid, socket_list, (x,abb.neg(l[j],N)), N)
		inter = abb.mult(self_pid, socket_list, (inter, (self_pid,i[j])), t, N, nB)
		l[j] = abb.add(self_pid, socket_list,(inter, l[j]) , N)
	return l


def secure_bellman_ford(self_pid, socket_list, G, src_v_ind, init_party_id, N, t, check_err):
	'''
	find shortest paths to all vertices from source vertex, find predecessors along path
	@arg		: self party id, list of party sockets, shared graph, initializer party to distribute shares of 0 and T
				  share of source vertex id, share of val, check for errors
	@return 	: shared predecessors, shared shortest paths
	'''
	V_num = len(G[0])
	p = []
	d = []
	n = len(socket_list)
	init_party = socket_list[init_party_id-1]
	# initialization
	T = 20 
	if self_pid == init_party_id:
		for i in xrange(V_num):
			p.append((self_pid, 0))
			d.append((self_pid, T))
	else:
		for i in xrange(V_num):
			p.append((self_pid, 0))
			d.append((self_pid, T))

	# Set threshold for checking if negative
	threshold = (self_pid, 255)
	# update distance of source vertex to 0
	d = update_element(self_pid, socket_list, d, src_v_ind, (self_pid,0), t, N)
	#print nr.reconstruct_secret(socket_list, d[0], self_pid, nB, N),
	#print nr.reconstruct_secret(socket_list, d[1], self_pid, nB, N)


	error_vec = []

	# iterative updates to distances and predecessors
	for i in xrange(V_num):
		for j in xrange(V_num):
			for k in xrange(V_num):
				y = abb.add(self_pid, socket_list, [d[k], abb.neg(d[j], N)], N)
				y = abb.add(self_pid, socket_list, [y, (self_pid,G[k][j])], N)
				#print nr.reconstruct_secret(socket_list, y, self_pid, nB, N),
				y_t = (y[0], y[1]+256 % N)
				x = abb.compare(self_pid, socket_list, (threshold, y_t), t, N, nB, (1,2), 8)
				if check_err:
					error_vec.append(abb.is_boolean(self_pid, socket_list, x, t, N, nB, (1,2)))
				x_y = abb.mult(self_pid, socket_list, (y,x), t, N, nB)

				#print nr.reconstruct_secret(socket_list, x, self_pid, nB, N),
				#print nr.reconstruct_secret(socket_list, x_y, self_pid, nB, N),
				
				d[j] = abb.add(self_pid, socket_list, [d[j], x_y], N)
				#print nr.reconstruct_secret(socket_list, d[j], self_pid, nB, N),
				prod_1 = abb.add(self_pid, socket_list, [(self_pid,1), abb.neg(x, N)], N)
				prod_1 = abb.mult(self_pid, socket_list, (prod_1,p[j]), t, N, nB)
				prod_2 = (x[1]*k)%N
				p[j] = abb.add(self_pid, socket_list, [prod_1, (self_pid,prod_2)], N)
				#print nr.reconstruct_secret(socket_list, p[j], self_pid, nB, N),
				print "iter:", i, j, k, "=>", i*(V_num**2)+j*V_num+k+1, "/", V_num**3

	if check_err:
		error_bool_sh = abb.rec_mult(self_pid, socket_list, error_vec, t, N, nB)
	else:
		error_bool_sh = (self_pid, 1)

	return p, d, error_bool_sh


def reconstruct_preds_dists(self_pid, socket_list, p, d, error_bool_sh, N):
	'''
	reconstruct predecessors, distances and error boolean
	'''
	p_vals = []
	d_vals = []
	for i in range(len(p)):
		p_vals.append(nr.reconstruct_secret(socket_list, p[i], self_pid, nB, N))
		d_vals.append(nr.reconstruct_secret(socket_list, d[i], self_pid, nB, N))

	error_bool = nr.reconstruct_secret(socket_list, error_bool_sh, self_pid, nB, N)
	return p_vals, d_vals, error_bool


def sec_bf_wrapper(self_pid, socket_list, G, src_v_ind, init_party_id, N):
	'''
	secure bellman ford wrapper function
	'''
	p, d, error_bool_sh = secure_bellman_ford(self_pid, socket_list, G, src_v_ind, init_party_id, N)
	p_vals, d_vals, error_bool = reconstruct_preds_dists(self_pid, socket_list, p, d, error_bool_sh, N)
	print p_vals, d_vals, error_bool
	if not error_bool:
		raise ValueError('encountered errors in abb operations; output may be incorrect')

	return p_vals, d_vals, error_bool
