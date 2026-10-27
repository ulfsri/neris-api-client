import importlib.metadata

try:
    __version__ = importlib.metadata.version("neris_api_client")
except importlib.metadata.PackageNotFoundError:
    # this is here for running the client in development mode
    # i.e. from src.neris_api_client import Config, NerisApiClient
    import pip._vendor.tomli as tomllib
    with open("pyproject.toml", "rb") as f:
        __version__ = tomllib.load(f)["project"]["version"]

from .client import *
from .config import *
