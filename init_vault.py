#!/usr/bin/env python
import os

from hvac import Client

from tools.vault import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_FILE = os.path.join(CURRENT_DIR, '.vault-init.json')
K8S_CA_CERT_FILE = os.path.join(CURRENT_DIR, '.kube-ca.pem')
vault = Client(url="https://localhost:8200", verify="ssl/certs/ca.pem")

vault_settings = init_vault(vault, SETTINGS_FILE)
unseal_vault(vault, vault_settings)

vault.token = vault_settings["root_token"]
vault.enable_secret_backend(backend_type='pki', mount_point='/pki', config={"max_lease_ttl": 760 * 24 * 60})

bundle = {}
with open(os.path.join(CURRENT_DIR, "ssl", "certs", "ca.pem")) as input:
    bundle['cert'] = input.read()
with open(os.path.join(CURRENT_DIR, "ssl", "certs", "ca-key.pem")) as input:
    bundle['key'] = input.read()

vault.write(path='/pki/config/ca', pem_bundle="{}\n{}".format(bundle['cert'], bundle['key']))

vault.write('/pki/roles/default', allow_any_name=False, allow_subdomains=True,
            allowed_domains="default.svc.cluster.local",
            ttl='768h')

vault.write('/pki/roles/servicemesh', allow_any_name=False, allow_subdomains=True,
            allowed_domains="default.svc.cluster.local,default.mesh",
            ttl='768h')

vault.write('/pki/roles/mongo', allow_any_name=False, allow_subdomains=True,
            allowed_domains="mongo.default.svc.cluster.local",
            client_flag=True,
            server_flag=True,
            ttl='768h')

vault.enable_auth_backend('kubernetes')
mongo_pki_policy = """
path "pki/issue/mongo" {
  capabilities = ["create","update"]
}
"""
vault.write('/sys/policy/pki/mongo', policy=mongo_pki_policy)

apps_pki_policy = """
path "pki/issue/servicemesh" {
  capabilities = ["update"]
}

path "pki/issue/default" {
  capabilities = ["update"]
}
"""
vault.write('/sys/policy/pki/apps', policy=apps_pki_policy)


k8s_cacert = read_file(K8S_CA_CERT_FILE)
vault.write('auth/kubernetes/config',
            kubernetes_host="https://kubernetes",
            kubernetes_ca_cert=k8s_cacert)

vault.write('auth/kubernetes/role/mongo-sa',
            bound_service_account_names=["mongo-sa"],
            bound_service_account_namespaces=["default"],
            ttl="768h",
            policies=["default", "pki/mongo"])

apps_roles = ["echo-server-sa","echo-client-sa"]
for app in apps_roles:
    vault.write('auth/kubernetes/role/{}'.format(app),
            bound_service_account_names=[app],
            bound_service_account_namespaces=["default"],
            ttl="768h",
            policies=["default", "pki/apps"])
