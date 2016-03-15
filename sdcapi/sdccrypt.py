import base64
import Crypto.Cipher.AES

class AESPKCS5(object):
    BS = 16
    pad = lambda s: s + (AESPKCS5.BS - len(s) % AESPKCS5.BS) * chr(AESPKCS5.BS - len(s) % AESPKCS5.BS).encode()
    unpad = lambda s : s[0:-s[-1]]

    @classmethod
    def new(cls, key):
        return cls(key)

    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = AESPKCS5.pad(raw)
        iv = self.key
        cipher = Crypto.Cipher.AES.new( self.key, Crypto.Cipher.AES.MODE_CBC, iv )
        return ( cipher.encrypt( raw ) )

    def decrypt( self, enc, sentinel = None ):
        iv = self.key
        cipher = Crypto.Cipher.AES.new(self.key, Crypto.Cipher.AES.MODE_CBC, iv )
        xxx = cipher.decrypt(enc)
        return AESPKCS5.unpad(xxx)


def base64Decrypt(data, alg, key):
    alg = alg.new(key)
    return alg.decrypt(base64.b64decode(data), None)

def base64Encrypt(data, alg, key):
    cipher = alg.new(key)
    return base64.b64encode(cipher.encrypt(data))

