#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 14:21:26

import net_share as ns
import sys
from time import sleep
from math import ceil, log

def share_secrets(secrets):
	t = 1
	#N = 110566836484895734954398231583463152069845275179779537530039974333624866315077
	#N = 314853400076558016540142136275780708481
	#N = 13317897048299897509
	N = 4190502817
	N = 104059
	#N = 36209
	nB = int(ceil(log(N)/(8*log(2))))
	# Create sockets
	parties = ns.connection_phase()
	for x in secrets:
		print "sharing secrect: "+str(x)
		sh = ns.gen_shares(3, t, x, N)
		print "shares: ",sh
		ns.distribute_secret(sh, parties, nB)
	return 

if __name__ == '__main__':
	x = int(sys.argv[1])
	y = int(sys.argv[2])
	share_secrets([x,y])


	# a = int(sys.argv[3])
	# b = int(sys.argv[4])
	# share_secrets([x,y,a,b])
