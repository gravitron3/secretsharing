# coding=utf8
from random import SystemRandom
import sys
import binascii
import qrcodesecret
sys.setrecursionlimit(1000000)

randgen = SystemRandom()


#Using mersenne primes as modulus for the finite field
#in which the polynomial lives. This allows for a small
#representation of the modulus. The only point of this is
#to make it easier for human to type in the modulus
#for secret reconstruction.
mersenne_exponents = [107, 127, 521, 607, 1279, 2203, 2281]


"""
secret - the secret that is supposed to be shared
n_needed - how many shares shall be needed to reconstruct the secret
k_total - how many shares shall exist in total
p - the modulus of the finite field"""
def split_secret(secret, n_needed, k_total, p):
	coefficients = []
	#the first coefficient is the secret		
	coefficients.append(secret)	
	for i in range(1, n_needed):
		coefficients.append(randgen.randrange(p-1))
	points = gen_points(k_total, coefficients)
	return points


"""returns k points on the polynomial that is determined by the given coefficients"""
def gen_points(k_total, coefficients):
	points = []
	if k_total < len(coefficients):
		exceptionText = ("Wrong k ("
			+ str(k_total)
			+ ") value or wrong number of coefficients ("
			+ str(len(coefficients))
			+ "): You need at least as many points as there"
			+ " are coefficients (i.e. degree + 1) in your "
			+ "polynomial in order to be able to reconstruct the secret")
		raise Exception(exceptionText)
	for i in range(1, k_total+1):
		points.append([i, polynomials_value_at(coefficients, i, p)])
	return points


"""returns the y-value of the polynomial determined by the given
coefficients at the given x-value"""
def polynomials_value_at(coefficients, x_value, p):
	y = 0
	for i in range(len(coefficients)):
			y += coefficients[i]*x_value**(i) % p
	return y

def lagrange_interpolation(points, p):
	result = 0
	for i in range(len(points)):
		
		prod = 1
		for j in range(len(points)):
			
			if j != i:
				prod = (prod * (0-points[j][0]) 
					* inverse(points[i][0]-points[j][0], p)) % p
			
		result = (result + points[i][1] * prod) % p
	return result

def reconstruct_secret(points, p):
	secret = lagrange_interpolation(points, p)
	if (secret >= p):
		raise Exception("secret is bigger than the modulus")
	return secret

# return (g, x, y) a*x + b*y = gcd(x, y)
def extended_euclid(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = extended_euclid(b % a, a)
        return (g, y - (b // a) * x, x)

# x = mulinv(b) mod n i.e. (x * b) % n == 1
def mulinv(b, n):
    g, x, _ = extended_euclid(b, n)
    if g == 1:
        return x % n	

def inverse(element, p):
	if (element < 0):
		element += p
	if (element == 0):
		raise Exception("Asked to calculate the inverse of 0...")
	return mulinv(element, p)

"""return the numerical representation of a text string in hex"""
def number_representation(string):
	return int(string.encode("hex"),16)

"""returns the text that is represented by number_representation in utf-8"""
def utf8_string(number_representation):
	hexrepr = str(hex(number_representation))
	hexrepr = hexrepr[2:]
	if hexrepr[len(hexrepr)-1] == "L":
		hexrepr = hexrepr[:len(hexrepr)-1]

	return str(hexrepr).decode("hex").decode("utf-8")

def get_all_subsets_of_size_n(n, main_set):
	subsets = []
	if (n == 1):
		for elem in main_set:
			subsets.append([elem])
	if (n > len(main_set)):
		return []
	new_main_set = list(main_set)
	for i in range(len(main_set)):
		subset_i = []
		elem_at_i = main_set[i]
		new_main_set.remove(elem_at_i)
		subset_i.append(elem_at_i)
		for subset_with_fixed_i in get_all_subsets_of_size_n(n-1, new_main_set):
			for element in subset_with_fixed_i:
				subset_i.append(element)
			subsets.append(subset_i)
			subset_i = []
			subset_i.append(elem_at_i)
	return subsets


"""Splits the secrect and tests whether the secret can be reconstructed from any
set of minimum needed shares. This is an unusual thing to do but it is of overall
importance to make sure that the secret can actually be reconstructed from the shares.
Only if the reconstruction works it is secure to delete the secret."""
def split_secret_and_check(secret, n_needed, k_total, p):
	points = split_secret(secret, n_needed, k_total, p)
	
	all_subsets = get_all_subsets_of_size_n(n_needed, points)
	for subset in all_subsets:
		reconstructed = reconstruct_secret(subset, p)
		if reconstructed != secret:
			raise Exception("I could not reconstruct the secret from the"
						+" shares. Please try again.")
			quit()
	return points

def find_smallest_possible_mersenne_exponent(secret_as_number):
	for exp in mersenne_exponents:
		if (2**exp)-1 > secret_as_number:
			return exp
	raise Exception("secret is too big for me")

if __name__ == "__main__":	
	secret = raw_input("enter secret that is supposed to be shared\n")
	e = find_smallest_possible_mersenne_exponent(number_representation(secret))
	p = 2**e-1
	n_needed = int( raw_input("enter number of shares needed to reconstruct the secret\n"))
	k_total = int (raw_input("enter the total amount of shares\n") )

	points = split_secret_and_check(number_representation(secret), n_needed, k_total, p)
	reconstructed = reconstruct_secret(points, p)


	description = raw_input("enter description:\n")
	qrcodesecret.generate_qr_codes(points)
	qrcodesecret.generate_website(points, description, e)
	qrcodesecret.generate_txt(points, "2**" + str(e) + "-1")
	qrcodesecret.generate_multiple_txt(points, "2**" + str(e) + "-1")
