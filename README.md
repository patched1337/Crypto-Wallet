# Crypto Wallet API
- FastAPI crypto wallet.

# Endpoints
```
/api/networks                           - Returns the avaliable wallet crypto networks.
/api/create                             - Creates a new wallet and returns all the info needed to maintian said wallet.
/api/create_child?network=xxx&xpub=xxx  - Creates a child address from your x-public-key.
/api/balance?network=xxx&address=xxx    - Returns the balance from the address.
```