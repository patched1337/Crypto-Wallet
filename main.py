"""
crypto wallet api.

author: patched1337@github.com
"""

import uvicorn
import requests
from pywallet import wallet
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

async def http_error(request, exc):
    return JSONResponse(
        {"message": exc.detail, "status_code": exc.status_code},
        status_code=exc.status_code,
    )

app = FastAPI(
    title="Crypto Wallet API",
    description="API for creating crypto wallets.",
    version="1.0",
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/api-config.json",
    exception_handlers={HTTPException: http_error}
)

class wallets:

    """
    simple little wrapper using pywallet and a few crypto apis.
    """

    def __init__(self) -> None:
        self.networks = ["BTC", "ETH", "LTC", "DASH", "DOGE"]

    def _create_wallet(self, network: str) -> dict:
        if not network.upper() in self.networks:
            raise HTTPException(status_code=404, detail="invalid network identifier")

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
            raise HTTPException(status_code=404, detail="invalid network identifier")

        child = wallet.create_address(
            network=network,
            xpub=x_public_key
        )

        return {"child_address": child["address"]}

    def _wallet_balance(self, network: str, address: str) -> dict:
        if not network.upper() in self.networks:
            raise HTTPException(status_code=404, detail="invalid network identifier")

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
                raise HTTPException(status_code=400, detail="unable to get address balance")

        if network.upper() == "ETH":
            csrf = requests.get("https://www.cointracker.io/wallet/ethereum")
            if "csrf_token" in csrf.text:
                csrf_token = csrf.text.split('"csrf_token" type="hidden" value="')[1].split('"')[0]
            else:
                raise HTTPException(status_code=400, detail="unable to get address balance")

            data = {"csrf_token": csrf_token, "address": address}
            r = requests.post("https://www.cointracker.io/wallet_balance/poll", data=data)
            if r.json()["success"]:
                return {"balance": r.json()["balance"], "usd": r.json()["usd_value"]}
            else:
                raise HTTPException(status_code=400, detail="unable to get address balance")

        if network.upper() == "LTC":
            r = requests.get("https://api.blockcypher.com/v1/ltc/main/addrs/%s" % (address))
            if "error" in r.text:
                raise HTTPException(status_code=400, detail="unable to get address balance")
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

        if network.upper() == "DASH":
            r = requests.get("https://api.blockcypher.com/v1/dash/main/addrs/%s" % (address))
            if "error" in r.text:
                raise HTTPException(status_code=400, detail="unable to get address balance")
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

        if network.upper() == "DOGE":
            r = requests.get("https://api.blockcypher.com/v1/doge/main/addrs/%s" % (address))
            if "error" in r.text:
                raise HTTPException(status_code=400, detail="unable to get address balance")
            else:
                return {"balance": r.json()["balance"], "unconfirmed": r.json()["unconfirmed_balance"]}

class Routes:
    """
    all the routes/endpoints for the crypto api.
    """

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
    """
    starts the fastapi server using uvicorn.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=True
    )