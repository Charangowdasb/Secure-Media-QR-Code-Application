"""
Shamir's Secret Sharing Algorithm Implementation

This module implements Shamir's Secret Sharing scheme which allows splitting
a secret into N shares such that any K shares can reconstruct the secret,
but K-1 or fewer shares reveal nothing about the secret.

Based on polynomial interpolation over a finite field.
"""

import random
from typing import List, Tuple
from utils import get_logger

logger = get_logger(__name__)


class ShamirSecretSharing:
    """
    Shamir's Secret Sharing implementation using Lagrange interpolation
    in GF(p) - Galois Field with prime modulus
    """
    
    def __init__(self, prime: int = None):
        """
        Initialize with a large prime for finite field arithmetic
        Default prime is a 256-bit prime for security
        """
        if prime is None:
            # Large 256-bit prime
            self.prime = 2**256 - 2**224 + 2**192 + 2**128 - 1
        else:
            self.prime = prime
        logger.info(f"ShamirSecretSharing initialized with prime: {self.prime}")

    def _split_secret(self, secret: int, k: int, n: int) -> List[Tuple[int, int]]:
        """
        Split secret into n shares, requiring k shares to reconstruct.
        
        Args:
            secret: The secret value to split
            k: Threshold - minimum shares needed to reconstruct
            n: Total number of shares to generate
            
        Returns:
            List of (x, y) tuples representing the shares
        """
        if k > n:
            raise ValueError("Threshold k cannot be greater than total shares n")
        if k < 2:
            raise ValueError("Threshold k must be at least 2")
        if n < k:
            raise ValueError("Total shares n must be at least equal to k")

        # Generate random coefficients for polynomial of degree k-1
        # Polynomial: f(x) = a_0 + a_1*x + a_2*x^2 + ... + a_(k-1)*x^(k-1)
        # where a_0 = secret
        coefficients = [secret] + [random.randint(0, self.prime - 1) for _ in range(k - 1)]
        
        logger.debug(f"Generated polynomial with {k} coefficients")

        # Evaluate polynomial at n different points (x from 1 to n)
        shares = []
        for x in range(1, n + 1):
            y = self._evaluate_polynomial(coefficients, x)
            shares.append((x, y))
        
        logger.info(f"Successfully split secret into {n} shares (threshold {k})")
        return shares

    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """
        Evaluate polynomial at point x using Horner's method
        f(x) = a_0 + a_1*x + a_2*x^2 + ... + a_n*x^n (mod prime)
        """
        result = 0
        for coef in reversed(coefficients):
            result = (result * x + coef) % self.prime
        return result

    def _lagrange_interpolation(self, shares: List[Tuple[int, int]], x: int = 0) -> int:
        """
        Reconstruct secret using Lagrange interpolation
        Evaluates the polynomial at x=0 (which gives the constant term = secret)
        
        Args:
            shares: List of (x, y) share tuples
            x: Point to evaluate at (0 for secret)
            
        Returns:
            The reconstructed secret (or polynomial value at x)
        """
        result = 0
        
        for i, (x_i, y_i) in enumerate(shares):
            # Calculate Lagrange basis polynomial L_i(x)
            numerator = 1
            denominator = 1
            
            for j, (x_j, y_j) in enumerate(shares):
                if i != j:
                    numerator = (numerator * (x - x_j)) % self.prime
                    denominator = (denominator * (x_i - x_j)) % self.prime
            
            # Calculate modular multiplicative inverse
            inv_denominator = self._mod_inverse(denominator, self.prime)
            
            # Add to result
            result = (result + y_i * numerator * inv_denominator) % self.prime
        
        return result

    def _mod_inverse(self, a: int, m: int) -> int:
        """
        Calculate modular multiplicative inverse using Extended Euclidean Algorithm
        Returns x such that (a * x) % m == 1
        """
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m

    def split(self, secret: str, k: int, n: int) -> List[str]:
        """
        Split a secret string into n shares
        
        Args:
            secret: The secret string to split
            k: Threshold - minimum shares needed to reconstruct
            n: Total number of shares to generate
            
        Returns:
            List of shares as hex strings
        """
        # Convert secret string to bytes and then treat as chunks
        secret_bytes = secret.encode('utf-8')
        
        # For large secrets, we'll process in chunks to avoid field overflow
        chunk_size = 16  # 128-bit chunks
        all_shares = [[] for _ in range(n)]
        
        for i in range(0, len(secret_bytes), chunk_size):
            chunk = secret_bytes[i:i+chunk_size]
            chunk_int = int.from_bytes(chunk, byteorder='big')
            
            # Split this chunk
            chunk_shares = self._split_secret(chunk_int, k, n)
            
            # Collect shares
            for share_idx, (x, y) in enumerate(chunk_shares):
                all_shares[share_idx].append((x, y))
        
        # Encode shares as strings with chunk separation
        shares_hex = []
        for share_list in all_shares:
            # Encode each (x,y) pair
            share_str = ",".join([f"{x}:{y}" for x, y in share_list])
            shares_hex.append(share_str)
        
        logger.info(f"Successfully split secret into {n} shares with {len(all_shares[0])} chunks (threshold {k})")
        return shares_hex

    def reconstruct(self, shares: List[str]) -> str:
        """
        Reconstruct the secret from shares
        
        Args:
            shares: List of share strings in "x:y,x:y,..." format (for multi-chunk)
            
        Returns:
            The reconstructed secret string
        """
        if not shares:
            raise ValueError("No shares provided")
        
        # Parse shares - handling multi-chunk format
        all_parsed_shares = []
        for share in shares:
            parsed = []
            pairs = share.split(',')
            for pair in pairs:
                parts = pair.split(':')
                if len(parts) != 2:
                    raise ValueError(f"Invalid share format: {pair}")
                try:
                    x = int(parts[0])
                    y = int(parts[1])
                    parsed.append((x, y))
                except ValueError:
                    raise ValueError(f"Invalid share format: {pair}")
            all_parsed_shares.append(parsed)
        
        # Reconstruct each chunk
        if not all_parsed_shares[0]:
            raise ValueError("No share data")
        
        num_chunks = len(all_parsed_shares[0])
        secret_bytes = b''
        
        for chunk_idx in range(num_chunks):
            # Extract chunk data from all shares
            chunk_shares = []
            for share_idx in range(len(all_parsed_shares)):
                if chunk_idx < len(all_parsed_shares[share_idx]):
                    chunk_shares.append(all_parsed_shares[share_idx][chunk_idx])
            
            if len(chunk_shares) < 2:
                raise ValueError("Insufficient shares for chunk reconstruction")
            
            # Reconstruct this chunk
            chunk_int = self._lagrange_interpolation(chunk_shares, x=0)
            
            # Convert to bytes - determine byte length
            byte_length = max(1, (chunk_int.bit_length() + 7) // 8)
            chunk_bytes = chunk_int.to_bytes(byte_length, byteorder='big')
            secret_bytes += chunk_bytes
        
        try:
            secret = secret_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            logger.error(f"Error decoding reconstructed secret: {e}")
            raise ValueError(f"Failed to reconstruct secret: {e}")
        
        logger.info("Successfully reconstructed secret from shares")
        return secret


def create_secret_sharer(prime: int = None) -> ShamirSecretSharing:
    """Factory function to create a ShamirSecretSharing instance"""
    return ShamirSecretSharing(prime)
