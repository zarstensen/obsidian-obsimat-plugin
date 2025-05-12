import json
import sys

expected_version = sys.argv[0]

MANIFEST_FILE = "manifest.json"

with open(MANIFEST_FILE, 'r') as file:
    manifest = json.load(file)

if expected_version == manifest['version']:
    print("Versions Match!")
else:
    print("Versions Do Not Match!")
    print(f"Manifest Version:\t{manifest['version']}")
    print(f"Expected Version:\t{expected_version}")
    sys.exit(-1)
