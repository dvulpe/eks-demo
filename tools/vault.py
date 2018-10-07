import json


def init_vault(vault_client, output_file):
    initialise_result = vault_client.initialize()
    with open(output_file, 'w') as vault_init_file:
        json.dump(initialise_result, vault_init_file)
    return initialise_result


def load_vault_keys(file):
    with open(file, 'r') as vault_init_file:
        return json.load(vault_init_file)


def unseal_vault(vault_client, vault_settings):
    print('Unsealing vault')
    for unseal_key in vault_settings['keys']:
        vault_client.unseal(unseal_key)
    print('Vault unsealed')


def read_file(file):
    with open(file, 'r') as source:
        return source.read()
