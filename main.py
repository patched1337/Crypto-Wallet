import uvicorn
import requests
from fastapi import FastAPI
from pywallet import wallet

app = FastAPI(
    title="Crypto Wallet API",
    description="API for creating crypto wallets.",
    version="1.0",
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/api-config.json"
)
class wallets:

    def __init__(self) -> None:
        self.networks = ["BTC", "ETH", "LTC", "DASH", "DOGE"]

    def _create_wallet(self, network: str) -> dict:
        if not network.upper() in self.networks:
            return {"message": "Invalid network"}

        seed = wallet.generate_mnemonic()
        created = wallet.create_wallet(network=network, seed=seed, children=0)

        information = {
            "network": created["coin"],
            "public_key": created["public_key"],
            "address": created["address"],
            "security": {
                "seed": seed,
                "private_key": created["private_key"],
                "x_private_key": created["xprivate_key"],
                "x_public_key": created["xpublic_key_prime"],
            },
            "extra": {
                "wif": created["wif"],
            },
        }

        return information

    def _create_child_wallet(self, network: str, x_public_key: str) -> dict:
        if not network.upper() in self.networks:
            return {"message": "Invalid network"}

        child = wallet.create_address(
            network=network,
            xpub=x_public_key
        )

        return {"child_address": child["address"]}

    def _wallet_balance(self, network: str, address: str) -> dict:
        if not network.upper() in self.networks:
            return {"message": "Invalid network"}

        if network.upper() == "BTC":
            r = requests.get("https://api.smartbit.com.au/v1/blockchain/address/%s" % (address))
            if r.json()["success"]:
                return {
                    "confirmed": {
                        "balance": r.json()["address"]["total"]["received"],
                        "spent": r.json()["address"]["unconfirmed"]["spent"],
                    },
                    "unconfirmed": {
                        "balance": r.json()["address"]["unconfirmed"]["received"],
                        "spent": r.json()["address"]["unconfirmed"]["spent"],
                    },
                }
            else:
                return r.json()

        if network.upper() == "ETH":
            csrf = requests.get("https://www.cointracker.io/wallet/ethereum")
            if "csrf_token" in csrf.text:
                csrf_token = csrf.text.split('"csrf_token" type="hidden" value="')[1].split('"')[0]
            else:
                return {"message": "failed to check wallet balance"}

            data = {"csrf_token": csrf_token, "address": address}
            r = requests.post("https://www.cointracker.io/wallet_balance/poll", data=data)
            if r.json()["success"]:
                return {"balance": r.json()["balance"], "usd": r.json()["usd_value"]}
            else:
                return r.json()

        if network.upper() == "LTC":
            r = requests.get("https://api.blockcypher.com/v1/ltc/main/addrs/%s" % (address))
            if "error" in r.text:
                return r.json()
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

        if network.upper() == "DASH":
            r = requests.get("https://api.blockcypher.com/v1/dash/main/addrs/%s" % (address))
            if "error" in r.text:
                return r.json()
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

        if network.upper() == "DOGE":
            r = requests.get("https://api.blockcypher.com/v1/doge/main/addrs/%s" % (address))
            if "error" in r.text:
                return r.json()
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

class Routes:

    @app.get("/api/networks")
    async def networks():
        return {"networks": wallets().networks}

    @app.post("/api/create")
    async def create_wallet(network: str):
        return wallets()._create_wallet(network)
    
    @app.post("/api/create_child")
    async def create_child(network: str, xpub: str):
        return wallets()._create_child_wallet(network, xpub)

    @app.get("/api/balance")
    async def wallet_balance(network: str, address: str):
        return wallets()._wallet_balance(network, address)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=True
    )