#!/usr/bin/env python
import os

from hvac import Client

from tools.vault import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_FILE = os.path.join(CURRENT_DIR, '.vault-init.json')

vault = Client(url="https://localhost:8200", verify="ssl/certs/ca.pem")
vault_settings = load_vault_keys(SETTINGS_FILE)
unseal_vault(vault, vault_settings)
