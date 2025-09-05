import pytest
import requests
import sys
import os
import importlib.util

# Add src folder to sys.path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

# Dynamically import config.py
spec = importlib.util.spec_from_file_location(
    "config",
    os.path.join(os.path.dirname(__file__), "../src/config.py")
)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

SCREAM_QUEENS_URLS = config.SCREAM_QUEENS_URLS


@pytest.mark.parametrize("actress, url", SCREAM_QUEENS_URLS.items())
def test_wiki_urls_status(actress, url):
  req = requests.get(url)
  assert req.status_code == 200, f'Error: {actress} ({url}) returned {
      req.status_code}'
