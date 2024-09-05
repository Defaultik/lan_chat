def encrypt(msg):
    encrypted = ""

    for char in msg:
        if char.isalpha():
            if char.islower():
                encrypted += chr((ord(char) - ord('a') + 5) % 26 + ord('a'))
            else:
                encrypted += chr((ord(char) - ord('A') + 5) % 26 + ord('A'))
        else:
            encrypted += char

    return encrypted


def decrypt(msg):
    decrypted = ""

    for char in msg:
        if char.isalpha():
            if char.islower():
                decrypted += chr((ord(char) - ord('a') - 5) % 26 + ord('a'))
            else:
                decrypted += chr((ord(char) - ord('A') - 5) % 26 + ord('A'))
        else:
            decrypted += char
    return decrypted