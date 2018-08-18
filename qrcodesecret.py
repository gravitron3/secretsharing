# Import QR Code library
import qrcode
import os


# Create qr code instance



def generate_qr_code(data_string, output_name):
	qr = qrcode.QRCode(
	    version = 1,
	    error_correction = qrcode.constants.ERROR_CORRECT_L,
	    box_size = 10,
	    border = 4,
	)
	qr.add_data(data_string)
	qr.make(fit=True)
	img = qr.make_image()
	img.save(output_name)

"""Saves QR-Codes for the given list in the specified directory"""
def generate_qr_codes(points, folder=None):
	images = []
	for point in points:
		image_name =  ""+str(point[0]) + ".png"
		full_path = image_name
		if (folder):
			full_path=os.path.join(folder, full_path)
		generate_qr_code(str(point), full_path)
		images.append(image_name)
	return images

def generate_website(shares, secret_description, used_mersenne_exponent):
	website_content = ("<!DOCTYPE html><html><head><title>" + secret_description 
		+ "</title></head>")
	website_content += "<style>\ndiv {\n\twhite-space: pre-wrap;\n}\n th, td {\n\ttext-align: left;\n\tpadding: 4px;\n}\ntr:nth-child(even) {background-color: #f2f2f2;}\n</style>"
	website_content += "<body><h1>"+ secret_description +"</h1>"
	website_content += '''<table style ="font-family:'Courier New'">'''
	#TODO cut path name
	folder = secret_description
	if not os.path.exists(folder):
		os.makedirs(folder)
	images = generate_qr_codes(shares, folder)

	for image_name in images:
		print image_name
		website_content += '<tr><td><img src="'+image_name+'" alt=share '+image_name+'><p>p = 2**' +str(used_mersenne_exponent)+ '-1</p></td><td><div>' + format_share_string(str(shares[images.index(image_name)])) + '</div></td></tr>'
	website_content += "</body></html>"
	
	website = open(os.path.join(folder,"printable_shares.html"), "w")
	website.write(website_content)
	website.close()

def generate_txt(shares, p_modulus_as_string):
	txt_file = open("shares.txt", "w")
	txt_file.write("p = " +p_modulus_as_string + "\n")
	for point in shares:
		txt_file.write(str(point[0]) + ", " + str(point[1])+"\n")
	txt_file.close()

def generate_multiple_txt(shares, p_modulus_as_string):
	for point in shares:
		txt_file = open(str(point[0])+".txt", "w")
		txt_file.write("p = " + p_modulus_as_string + "\n")
		txt_file.write(str(point[0]) + ", " + str(point[1])+"\n")
		txt_file.close()
	
def format_share_string(number_string):
	formatted = "("
	formatted += number_string.partition(",")[0][1:] + ",\n"
	second_part = number_string.partition(", ")[2]
	i = 0
	readable_offset = 5
	while i+readable_offset < len(second_part):
		formatted += second_part[i:i+readable_offset] + " "
		i+= readable_offset
	if i < len(second_part):
		formatted += second_part[i:]
	if formatted[len(formatted)-1] == "]":
		s = list(formatted)
		s.pop()
		s.append(")")
		formatted = "".join(s)
	formatted = formatted.replace('L', '')
	return formatted
	
