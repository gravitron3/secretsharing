import secretsharing
import sys
import csv

shares_file_name = ""

if len(sys.argv) <= 1:
	shares_file_name = raw_input("enter filename of shares: ")
else:
	shares_file_name = sys.argv[1]

points =[]
p = 0
with open(shares_file_name, 'rb') as csvfile:
	filereader = csv.reader(csvfile)
	rows = []
	for row in filereader:
		rows.append(row)

	exp = rows[0][0].split("**")[1]
	exp = exp.split("-")[0]
	exp = int(exp)
	print exp
	
	p = 2**int(exp) - 1
	print p
	rows.pop(0)
	for row in rows:
		point = [int(row[0]), int(row[1])]
		points.append(point)
print points

print secretsharing.reconstruct_secret(points,p)
print secretsharing.utf8_string(secretsharing.reconstruct_secret(points,p))



