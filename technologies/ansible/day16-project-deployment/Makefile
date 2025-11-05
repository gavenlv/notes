# Makefile for Ansible Project Deployment

# Variables
ANSIBLE_CMD = ansible-playbook
INVENTORY_DEV = inventory/development
INVENTORY_STG = inventory/staging
INVENTORY_PROD = inventory/production
PLAYBOOK_SITE = playbooks/site.yml
PLAYBOOK_DEV = playbooks/deploy-development.yml
PLAYBOOK_STG = playbooks/deploy-staging.yml
PLAYBOOK_PROD = playbooks/deploy-production.yml

# Default target
.PHONY: help
help:
	@echo "Ansible Project Deployment Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help            Show this help message"
	@echo "  deploy-dev      Deploy to development environment"
	@echo "  deploy-stg      Deploy to staging environment"
	@echo "  deploy-prod     Deploy to production environment"
	@echo "  deploy-all      Deploy to all environments"
	@echo "  check-dev       Check development environment"
	@echo "  check-stg       Check staging environment"
	@echo "  check-prod      Check production environment"
	@echo "  lint            Lint playbooks"
	@echo "  encrypt-vault   Encrypt vault file"
	@echo "  decrypt-vault   Decrypt vault file"

# Deployment targets
.PHONY: deploy-dev
deploy-dev:
	$(ANSIBLE_CMD) -i $(INVENTORY_DEV) $(PLAYBOOK_DEV)

.PHONY: deploy-stg
deploy-stg:
	$(ANSIBLE_CMD) -i $(INVENTORY_STG) $(PLAYBOOK_STG)

.PHONY: deploy-prod
deploy-prod:
	$(ANSIBLE_CMD) -i $(INVENTORY_PROD) $(PLAYBOOK_PROD)

.PHONY: deploy-all
deploy-all: deploy-dev deploy-stg deploy-prod

# Check targets
.PHONY: check-dev
check-dev:
	ansible -i $(INVENTORY_DEV) all -m ping

.PHONY: check-stg
check-stg:
	ansible -i $(INVENTORY_STG) all -m ping

.PHONY: check-prod
check-prod:
	ansible -i $(INVENTORY_PROD) all -m ping

# Lint target
.PHONY: lint
lint:
	ansible-lint $(PLAYBOOK_SITE) $(PLAYBOOK_DEV) $(PLAYBOOK_STG) $(PLAYBOOK_PROD)

# Vault targets
.PHONY: encrypt-vault
encrypt-vault:
	ansible-vault encrypt group_vars/vault

.PHONY: decrypt-vault
decrypt-vault:
	ansible-vault decrypt group_vars/vault

# Install dependencies
.PHONY: install-deps
install-deps:
	pip install -r requirements.txt

# Clean targets
.PHONY: clean
clean:
	rm -f *.retry
	rm -f logs/*.log