import asyncio

from app.infrastructure.storage.local import LocalStorage


async def main():

    storage = LocalStorage()

    print("Storage initialized")

    print("Testing storage layer...")


if __name__ == "__main__":
    asyncio.run(main())
    
    
    #C:\Users\Laptop Arena\OneDrive\Documents\Research Intelligence Platform\app\infrastructure\storage\local.py