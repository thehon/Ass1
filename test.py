import string
from Crypto.Hash import MD5
import numpy as np

salt = "8b283e8957f744ae5a1a6add05fc354f"
hashed_password = 'e00cf25ad42683b3df678c61f42c6bda'
salted_hashed_password = MD5.new((hashed_password + salt).encode()).hexdigest()
print(salted_hashed_password)

def initialise_tfa(seed, n_init=1):
    hash = MD5.new(seed.encode()).hexdigest()[:4]
    for _ in range(n_init):
        hash = update_tfa(hash)
    return hash

def update_tfa(hash):
    hash = MD5.new(hash.encode()).hexdigest()[:4]
    return hash

for i in range(0,5):
    two_factor_init_n = i
    two_factor = initialise_tfa(salted_hashed_password, two_factor_init_n)
    print(two_factor)