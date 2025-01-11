# Check if the token expiry
def valid_token():
    global token_expiry
    return token_dacces is not None and time.time()< token_expiry