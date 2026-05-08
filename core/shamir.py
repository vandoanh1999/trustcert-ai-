"""
Genesis Core V8: Vendored Shamir's Secret Sharing

This module is a self-contained, vendored implementation of the 'secret-sharing'
library to resolve critical installation issues in sandboxed environments.

Full credit for the cryptographic implementation goes to the original author.
This code is sourced from: https://github.com/shea256/secret-sharing
Released under the MIT License.
"""

import six
from six.moves import range
import string

# --- Helper functions originally from utilitybelt ---
def int_to_charset(n, charset):
    if n < 0:
        raise ValueError("n must be a positive integer")
    if n == 0:
        return charset[0]
    output = ""
    while n > 0:
        n, digit = divmod(n, len(charset))
        output += charset[digit]
    return output[::-1]

def charset_to_int(s, charset):
    output = 0
    for char in s:
        output = output * len(charset) + charset.find(char)
    return output

# --- Core Polynomial Logic (originally polynomial.py) ---

def random_polynomial(degree, intercept, upper_bound):
    if degree < 0:
        raise ValueError('Degree must be a non-negative integer.')
    coefficients = [intercept]
    for i in range(degree):
        random_coeff = six.integer_types[-1].from_bytes(
            six.binary_type(string.printable.encode('ascii')),
            byteorder='big'
        ) % upper_bound
        coefficients.append(random_coeff)
    return coefficients

def get_polynomial_points(coefficients, num_points, upper_bound):
    points = []
    for x in range(1, num_points + 1):
        y = 0
        for i in range(len(coefficients)):
            y += coefficients[i] * (x ** i)
        points.append((x, y % upper_bound))
    return points

def modular_inverse(a, m):
    if six.PY2:
        return pow(a, m - 2, m)
    return pow(a, -1, m)

def lagrange_interpolate(x, x_coords, y_coords, upper_bound):
    y = 0
    for i in range(len(x_coords)):
        li = 1
        for j in range(len(x_coords)):
            if i != j:
                num = x - x_coords[j]
                den = x_coords[i] - x_coords[j]
                li = (li * num * modular_inverse(den, upper_bound)) % upper_bound
        y = (upper_bound + y + (y_coords[i] * li)) % upper_bound
    return y

# --- Main Sharer Class (originally sharing.py) ---

class SecretSharer(object):
    """
    A class for splitting a secret into shares and recovering it from a subset of shares.
    """
    prime = 115792089237316195423570985008687907853269984665640564039457584007913129639747
    share_charset = string.hexdigits[0:16]

    def __init__(self):
        pass

    @classmethod
    def split_secret(cls, secret_string, share_threshold, num_shares):
        if share_threshold > num_shares:
            raise ValueError("Secret threshold must be less than or equal to the number of shares.")
        secret_int = charset_to_int(secret_string, cls.share_charset)
        if secret_int > cls.prime:
            raise ValueError("Secret is too long for the prime modulus.")
        coefficients = random_polynomial(share_threshold - 1, secret_int, cls.prime)
        points = get_polynomial_points(coefficients, num_shares, cls.prime)
        shares = []
        for point in points:
            share = int_to_charset(point[0], cls.share_charset).zfill(1) + "-" + \
                int_to_charset(point[1], cls.share_charset)
            shares.append(share)
        return shares

    @classmethod
    def recover_secret(cls, shares):
        if not isinstance(shares, list):
            raise ValueError("Shares must be a list of strings.")
        x_coords, y_coords = [], []
        for share in shares:
            parts = share.split('-')
            x_coords.append(charset_to_int(parts[0], cls.share_charset))
            y_coords.append(charset_to_int(parts[1], cls.share_charset))
        free_coefficient = lagrange_interpolate(0, x_coords, y_coords, cls.prime)
        secret_string = int_to_charset(free_coefficient, cls.share_charset)
        if len(secret_string) % 2 != 0:
            secret_string = "0" + secret_string
        return secret_string

class PlaintextToHexSecretSharer(SecretSharer):
    """
    Wrapper for SecretSharer that handles plain text.
    """
    @classmethod
    def split_secret(cls, secret_string, share_threshold, num_shares):
        secret_hex = secret_string.encode('utf8').hex()
        return super(PlaintextToHexSecretSharer, cls).split_secret(
            secret_hex, share_threshold, num_shares)

    @classmethod
    def recover_secret(cls, shares):
        secret_hex = super(PlaintextToHexSecretSharer, cls).recover_secret(shares)
        return bytes.fromhex(secret_hex).decode('utf8')
