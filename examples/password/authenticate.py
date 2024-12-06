from dotenv import load_dotenv
from src.neris_api_client import NerisApiClient, Config

if __name__ == "__main__":
  load_dotenv()  
  client = NerisApiClient()

  client._update_auth()
  print(client.tokens)

  