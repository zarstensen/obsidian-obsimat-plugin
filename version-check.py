import json
import sys

expected_version = sys.argv[0]

MANIFEST_FILE = "manifest.json"

with open(MANIFEST_FILE, 'r') as file:
    manifest = json.load(file)

sys.exit(expected_version == manifest['version'])
