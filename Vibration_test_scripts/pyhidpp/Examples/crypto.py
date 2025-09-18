from pyhidpp.security import AESCipher


encryption = AESCipher()

decrypted = encryption.decrypt("MPM322")

print(decrypted)
