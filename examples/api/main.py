from dotenv import load_dotenv
from src.neris_api_client import NerisApiClient

if __name__ == "__main__":
  load_dotenv()
  client = NerisApiClient()

  client.create_api_integration("VN00000000", "Api integration Test")
  print(client.tokens)
  