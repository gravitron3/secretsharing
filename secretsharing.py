# coding=utf8
from random import SystemRandom
import sys
import binascii
import qrcodesecret
sys.setrecursionlimit(1000000)

randgen = SystemRandom()



mersenne_exponents = {127, 521, 607, 1279, 2203}



def split_secret(secret, n_needed, k_total, p):
	coefficients = []
	coefficients.append(secret)	
	for i in range(1, n_needed):
		#the first coefficient IS the secret		
		coefficients.append(randgen.randrange(p-1))
	points = gen_points(k_total, coefficients)
	return points


"""returns k points on the polynomial that is determined by the given coefficients"""
def gen_points(k_total, coefficients):
	points = []
	if k_total < len(coefficients):
		exeptionText = ("Wrong k ("
			+ str(k_total)
			+ ") value or wrong number of coefficients ("
			+ str(len(coefficients))
			+ "): You need at least as many points as there are coefficients (i.e. degree + 1) in your polynomial in order to be able to reconstruct the secret")
		raise Exception(exeptionText)
	for i in range(1, k_total+1):
		points.append([i, polynomials_value_at(coefficients, i, p)])
	return points


"""returns the y-value of the polynomial determined by the given coefficients at the given x-value"""
def polynomials_value_at(coefficients, x_value, p):
	y = 0
	for i in range(len(coefficients)):
			y += coefficients[i]*x_value**(i) % p
	return y

def reconstruct_secret(points, p):
	secret = 0
	print "have these points:"
	print points
	print "entering loop"
	for i in range(len(points)):
		print"\t" + str(i)
		prod = 1
		print "\t entering inner loop"
		for j in range(len(points)):
			print "\t\t" + str(j)
			if j != i:
				prod = (prod * (0-points[j][0]) 
					* inverse(points[i][0]-points[j][0], p)) % p
			print "\t\tprod is now:" + str(prod)
		secret = (secret + points[i][1] * prod) % p
		print "\t secret is now: " + str(secret)
	if (secret >= p):
		raise Exception("secret is bigger than the modulus")
	return secret

# return (g, x, y) a*x + b*y = gcd(x, y)
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

# x = mulinv(b) mod n, (x * b) % n == 1
def mulinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n	

def inverse(element, p):
	if (element < 0):
		element += p
		#raise Exception("Asked to calculate the inverse of " + str(element) + " which is a negative number. But we don't use negative numbers in our field arithmetic. Something in your code is wrong")
	if (element == 0):
		raise Exception("Asked to calculate the inverse of 0...")
	return mulinv(element, p)

"""return the numerical representation of a string in hex"""
def number_representation(string):
	return int(string.encode("hex"),16)

def utf8_string(number_representation):
	hexrepr = str(hex(number_representation))
	hexrepr = hexrepr[2:]
	if hexrepr[len(hexrepr)-1] == "L":
		hexrepr = hexrepr[:len(hexrepr)-1]
	print hexrepr
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
set of minimum needed shares. This is an unusual thing to do for a function. Normally
you would expect a programme to work correctly and be well tested. However in this case
I want to provide an additional mechanism to make sure your secret isn't lost due to
bugs or hardware failure during the construction of the shares."""
def split_secret_and_check(secret, n_needed, k_total, p):
	points = split_secret(secret, n_needed, k_total, p)
	
	all_subsets = get_all_subsets_of_size_n(n_needed, points)
	for subset in all_subsets:
		reconstructed = reconstruct_secret(subset, p)
		print subset
		print "checking... got " + str(reconstructed)
		if reconstructed != secret:
			raise Exception("I could not reconstruct the secret from the"
						+" shares. Trying again might solve the"
						+" problem due to randomness")
			quit()
	return points

def find_smallest_possible_mersenne_exponent(secret_as_number):
	for exp in mersenne_exponents:
		if (2**exp)-1 > secret_as_number:
			return exp
	raise Exception("secret is too big")

if __name__ == "__main__":	
	secret = raw_input("enter secret that is supposed to be shared\n")
	print "secret: " + secret
	print "number representation of secret: " + str(number_representation(secret))
	e = find_smallest_possible_mersenne_exponent(number_representation(secret))
	p = 2**e-1
	print "will choose p = " + str(p)
	n_needed = int( raw_input("enter number of shares needed to reconstruct the secret\n"))
	k_total = int (raw_input("enter the total amount of shares\n") )

	points = split_secret_and_check(number_representation(secret), n_needed, k_total, p)
	print "secret will be split to 5 out of 10 shares..."
	print "shares:"
	print points
	reconstructed = reconstruct_secret(points, p)
	print "rec as number: " + str(reconstructed)
	print "reconstructed secret: " + utf8_string(reconstructed)

	images = []
	for point in points:
		image_name =  ""+str(point[0]) + ".png"
		qrcodesecret.generate_qr_code(str(point), image_name)
		images.append(image_name)

	description = raw_input("enter description:\n")
	qrcodesecret.generate_website(images, points, description, e)
	qrcodesecret.generate_txt(points, "2**" + str(e) + "-1")
	qrcodesecret.generate_multiple_txt(points, "2**" + str(e) + "-1")
