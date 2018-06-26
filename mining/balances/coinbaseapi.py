from coinbase.wallet.client import Client

class Coinbase(Client):

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = Client( api_key, secret_key)

    def __call__(self):
        return self.client.get_accounts()

    def accounts(self):
        return self.client.get_accounts()
