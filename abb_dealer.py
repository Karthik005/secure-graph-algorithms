#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 14:21:26

import net_share as ns
import sys

def share_secret(x):
	t = 1
	N = 104059
	# Create sockets
	parties = ns.connection_phase()
	print "sharing secrect: "+str(x)
	sh = ns.gen_shares(3, t, x, N)
	print sh
	ns.distribute_secret(sh, parties, 20)
	return 

if __name__ == '__main__':
	x = int(sys.argv[1])
	y = int(sys.argv[2])
	share_secret(x)
	share_secret(y)
