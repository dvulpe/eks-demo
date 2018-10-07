#!/usr/bin/env bash

set -euo pipefail

mkdir -p certs

echo "Generating CA cert"
cfssl gencert -initca ca-csr.json | cfssljson -bare certs/ca

echo "Generating Vault cert"
cfssl gencert -ca=certs/ca.pem -ca-key=certs/ca-key.pem -config=ca-config.json -profile=server vault.json | cfssljson -bare certs/vault
