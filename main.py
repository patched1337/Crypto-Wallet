import uvicorn
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
            return {"message": "Invalid network", "data": {"networks": self.networks}}

        seed = wallet.generate_mnemonic()
        created = wallet.create_wallet(network=network, seed=seed, children=0)

class Routes:

    @app.get("/api/networks")
    async def networks():
        return {"networks": wallets().networks}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=80,
        reload=True
    )