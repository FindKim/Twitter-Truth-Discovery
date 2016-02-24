#!/usr/bin/env python

'''
Kim Ngo
Professor Dong Wang
CSE40437 - Social Sensing
23 February 2016

Accurately ascertain both the correctness of each tweet and the reliability of each Twitter user.

Usage: twitter-truth-discovery.py [sensing matrix file] [output file]
'''

import sys

GROUND_TRUTH_FILE = 'GroundTruth_File'

def readSensingMatrixFile(filename):
	matrix = {}
	f = open(filename, 'r')
	for line in f:
		source_id, measured_variable_id = [int(x) for x in line.split(',')]
		if source_id not in matrix:
			matrix[source_id] = {}
		matrix[source_id][measured_variable_id] = 1
	f.close()
	return matrix

def printMatrix(matrix):
	for source_id in matrix:
		print str(source_id) + ',' + ','.join('%d:%d' % (idx, val) for idx, val in enumerate(matrix[source_id]))


class TruthDiscovery():
	def __init__(self, matrix):
		self.matrix = matrix
		self.num_sources = len(matrix)
		self.num_measured_variables = self.calcTotNumMeasuredVariables()
		self.a = self.initAi()
		self.b = self.initBi()
		self.d = 0.5 # Algorithm line 1
		self.Z = dict.fromkeys(range(1,self.num_measured_variables+2)) # Computed values from equation 11
		self.H = dict.fromkeys(range(1,self.num_measured_variables+2)) # Optimal decision vector converged from Z(t,j)
		self.E = dict.fromkeys(self.matrix.keys()) # Optimal estimation vector of source reliability

	def numMeasuredVariables(self, source_id):
		return len(self.matrix[source_id])

	def calcTotNumMeasuredVariables(self):
		# Goes through matrix to find number of measured variables
		# by taking max of the last variable for each source (assumes sorted)
		max_var = 0
		for source_id in self.matrix:
			sorted_measured_variables = sorted(self.matrix[source_id].keys())
			max_var = max(max_var, sorted_measured_variables[-1])
		return max_var-1

	def calcSi(self, i):
		# num reports from si / total num of measured variables
		return len(self.matrix[i]) / float(self.num_measured_variables)

	def initAi(self):
		# Algorithm line 1; ai = si
		a = {}
		for i in self.matrix.keys():
			a[i] = self.calcSi(i)
		return a

	def initBi(self):
		# Algorithm line 1; bi = si * 0.5
		b = {}
		for i in self.matrix.keys():
			b[i] = self.calcSi(i) * 0.5
		return b

	def calcNextAi(self, s):
		# Equation 17
		numerator = sum([self.Z[j] for j in self.Z if j in self.matrix[s]])
		denominator = sum(self.Z.values())
		return numerator / float(denominator)

	def calcNextBi(self, s):
		# Equation 17
		Ki = self.numMeasuredVariables(s)
		N = self.num_measured_variables
		numerator = sum([self.Z[j] for j in self.Z if j in self.matrix[s]])
		denominator = sum(self.Z.values())
		return (Ki - numerator) / float(N - denominator)

	def calcNextDi(self, s):
		# Equation 17
		numerator = sum(self.Z.values())
		return numerator / float(self.num_measured_variables)

	def calcA(self, j):
		# Equation 12
		# Conditional probability regarding observations about the jth measured variable
		# and current estimation of the parameter theta given the jth measured variable
		# is true
		PI = 1
		for i in self.matrix:
			if j in self.matrix[i]:
				PI *= self.a[i]
			else:
				PI *= (1-self.a[i])
		return PI

	def calcB(self, j):
		# Equation 12
		# Conditional probability regarding observations about the jth measured variable
		# and current estimation of the parameter theta given the jth measured variable
		# is false
		PI = 1
		for i in self.matrix:
			if j in self.matrix[i]:
				PI *= self.b[i]
			else:
				PI *= (1-self.b[i])
		return PI

	def calcZ(self, j):
		# Equation 11
		numerator = self.calcA(j) * self.d
		denominator = self.calcA(j) * self.d + self.calcB(j) * (1 - self.d)
		return numerator / float(denominator)

	def calcSourceReliability(self, s):
		# Equation 5
		return self.a[s] * self.d / float(self.calcSi(s))

	def expectationMaximization(self):
		t = 0
		while t < 20:
			# Expectation step: Compute the expected log likelihood function where the expectation is taken with respect
			# to the computed conditional distribution of the latent variables given the current settings and observed data. 

			# Algorithm lines 3 - 5
			for j in self.Z:
				self.Z[j] = self.calcZ(j)

			# Maximization step: Find the parameters that maximize the Q function in the E-step to be used as the estimate
			# of theta for the next iteration.

			# Algorithm lines 6 - 10
			for i in self.matrix:
				self.a[i] = self.calcNextAi(i)
				self.b[i] = self.calcNextBi(i)
				self.d = self.calcNextDi(i)
			t += 1

		# Algorithm lines 15 - 21
		for j in self.Z:
			if self.Z[j] >= 0.5:
				self.H[j] = 1
			else:
				self.H[j] = 0

		# Algorithm lines 22 - 24
		for i in self.matrix:
			self.E[i] = self.calcSourceReliability(i)

	def verifyTruth(self):
		# Only use to verify testing files
		truth_dict = {}
		f = open(GROUND_TRUTH_FILE)
		for line in f:
			measured_variable_id, correctness_indicator = line.split(',')
			truth_dict[int(measured_variable_id)] = int(correctness_indicator)
		f.close()
		for j in truth_dict:
			if truth_dict[j] != self.H[j]:
				print 'Incorrect:', j, truth_dict[j], self.H[j]

	def writeOutput(self, filename):
		# Writes each line in the format "measured variable ID, 1 or 0",
		# where 1 indicates the variable is true and 0 indicates it is false
		f = open(filename, 'w')
		for j in self.H:
			f.write(str(j) + ',' + str(self.H[j]) + '\n')
		f.close()

def main():
	if len(sys.argv) != 3:
		print >> sys.stderr, 'Usage: %s [sensing matrix file] [output file]' % (sys.argv[0])
		exit(-1)

	matrix = readSensingMatrixFile(sys.argv[1])
	td = TruthDiscovery(matrix)
	td.expectationMaximization()
	#td.verifyTruth()
	td.writeOutput(sys.argv[2])


if __name__ == '__main__':
	main()

