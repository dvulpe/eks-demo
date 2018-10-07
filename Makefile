DEFAULT: venv

clean:
	@rm -rf .venv

venv: .venv/bin/activate

.venv/bin/activate: requirements.txt
	@test -d .venv || virtualenv .venv
	@.venv/bin/pip install -U pip wheel setuptools
	@.venv/bin/pip install -Ur requirements.txt
	@touch .venv/bin/activate

vault-init: venv
	@.venv/bin/python init_vault.py

vault-unseal: venv
	@.venv/bin/python unseal_vault.py

vault-login: venv
	@cat .vault-init.json  | jq -r .root_token | vault login -