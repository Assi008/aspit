import base64

def encode_password():
    AUTH_STRING = 'username:password'
    encoded_pass = base64.b64encode(AUTH_STRING.encode()).decode()
    print(encoded_pass)  # print the result to the stdout

if __name__ == "__main__":
    encode_password()