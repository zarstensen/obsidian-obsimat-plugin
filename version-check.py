import json
import sys

expected_version = sys.argv[1]

MANIFEST_FILE = "manifest.json"

with open(MANIFEST_FILE, 'r') as file:
    manifest = json.load(file)

if expected_version == manifest['version']:
    print("Versions Match!")
else:
    print("Versions Do Not Match!")
    print(f"Expected Version:\t{expected_version}")
    print(f"Manifest Version:\t{manifest['version']}")
    sys.exit(-1)
