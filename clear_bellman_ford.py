import sys

if __name__ == '__main__':
	G = [[int(val) for val in line.split()] for line in open('graph')]
	N = 104059
	l = 8

	if len(sys.argv) < 2:
		print "Usage:", sys.argv[0], "<s>"
		sys.exit(1)
	s = int(sys.argv[1])
	
	p = [0 for i in range(0, len(G))]
	d = [2**8 for i in range(0, len(G))]

	d[s] = 0

	for j in range(0, len(G)):
		for i in range(0, len(G)):
			for e in range(0, len(G)):
				y = d[e] - d[i] + G[e][i]
				x = (y+2**l) < 2**l
				d[i] = d[i] + x*y
				p[i] = (1-x)*p[i] + x*e
	
	print 'Distances:', d
	print 'Predecessors:', p
