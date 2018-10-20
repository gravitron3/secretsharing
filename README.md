# secretsharing
Python implementation of Shamir's secret sharing scheme as descibed in Shamir, A. (1979). How to share a secret. Communications of the ACM, 22(11), 612-613.

The tool is a simple command line program that splits a secret on the desired amount of shares. The secret can then be reconstructed from the needed amount of shares. 

This can for example be used to store Bitcoin private keys or mnemonic seeds more securely.

# dependencies
qrcode
Pillow
