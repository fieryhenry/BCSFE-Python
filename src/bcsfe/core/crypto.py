import enum
import hashlib
import hmac
import random
from typing import Optional
from bcsfe.core import io


class HashAlgorithm(enum.Enum):
    """An enum representing a hash algorithm."""

    MD5 = enum.auto()
    SHA1 = enum.auto()
    SHA256 = enum.auto()


class Hash:
    """A class to hash data."""

    def __init__(self, algorithm: HashAlgorithm):
        """Initializes a new instance of the Hash class.

        Args:
            algorithm (HashAlgorithm): The hash algorithm to use.
        """
        self.algorithm = algorithm

    def get_hash(
        self,
        data: "io.data.Data",
        length: Optional[int] = None,
    ) -> "io.data.Data":
        """Gets the hash of the given data.

        Args:
            data (io.data.Data): The data to hash.
            length (Optional[int], optional): The length of the hash. Defaults to None.

        Raises:
            ValueError: Invalid hash algorithm.

        Returns:
            io.data.Data: The hash of the data.
        """
        if self.algorithm == HashAlgorithm.MD5:
            hash = hashlib.md5()
        elif self.algorithm == HashAlgorithm.SHA1:
            hash = hashlib.sha1()
        elif self.algorithm == HashAlgorithm.SHA256:
            hash = hashlib.sha256()
        else:
            raise ValueError("Invalid hash algorithm")
        hash.update(data.get_bytes())
        if length is None:
            return io.data.Data(hash.digest())
        return io.data.Data(hash.digest()[:length])


class Random:
    """A class to get random data"""

    @staticmethod
    def get_bytes(length: int) -> bytes:
        """Gets random bytes.

        Args:
            length (int): The length of the bytes.

        Returns:
            bytes: The random bytes.
        """
        return bytes(random.getrandbits(8) for _ in range(length))

    @staticmethod
    def get_alpha_string(length: int) -> str:
        """Gets a random string of the given length.

        Args:
            length (int): The length of the string.

        Returns:
            str: The random string.
        """
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def get_hex_string(length: int) -> str:
        """Gets a random hex string of the given length.

        Args:
            length (int): The length of the string.

        Returns:
            str: The random string.
        """
        characters = "0123456789abcdef"
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def get_digits_string(length: int) -> str:
        """Gets a random digits string of the given length.

        Args:
            length (int): The length of the string.

        Returns:
            str: The random string.
        """
        characters = "0123456789"
        return "".join(random.choice(characters) for _ in range(length))


class Hmac:
    def __init__(self, algorithm: HashAlgorithm):
        self.algorithm = algorithm

    def get_hmac(self, key: "io.data.Data", data: "io.data.Data") -> "io.data.Data":
        if self.algorithm == HashAlgorithm.MD5:
            alg = hashlib.md5
        elif self.algorithm == HashAlgorithm.SHA1:
            alg = hashlib.sha1
        elif self.algorithm == HashAlgorithm.SHA256:
            alg = hashlib.sha256
        else:
            raise ValueError("Invalid hash algorithm")
        hmac_data = hmac.new(key.get_bytes(), data.get_bytes(), digestmod=alg).digest()
        return io.data.Data(hmac_data)


class NyankoSignature:
    def __init__(self, inquiry_code: str, data: str):
        self.inquiry_code = inquiry_code
        self.data = data

    def generate_signature(self) -> str:
        """Generates a signature from the inquiry code and data.

        Returns:
            str: The signature.
        """
        random_data = Random.get_hex_string(64)
        key = self.inquiry_code + random_data
        hmac = Hmac(HashAlgorithm.SHA256)
        signature = hmac.get_hmac(io.data.Data(key), io.data.Data(self.data))

        return random_data + signature.to_hex()

    def generate_signature_v1(self) -> str:
        """Generates a signature from the inquiry code and data.

        Returns:
            str: The signature.
        """

        data = self.data + self.data  # repeat data for some reason
        random_data = Random.get_hex_string(40)
        key = self.inquiry_code + random_data
        hmac = Hmac(HashAlgorithm.SHA1)
        signature = hmac.get_hmac(io.data.Data(key), io.data.Data(data))

        return random_data + signature.to_hex()
