# Prefer zsh, fall back to bash
SHELL := $(shell command -v zsh 2>/dev/null || command -v bash)

# Only set ZDOTDIR if the Make shell is zsh
ifeq ($(notdir $(SHELL)),zsh)
  export ZDOTDIR := $(CURDIR)/.devcontainer/scripts
endif

# Tool discovery
K3D      := $(shell command -v k3d)
KUBECTL  := $(shell command -v kubectl)
HELM     := $(shell command -v helm)
SKAFFOLD := $(shell command -v skaffold)
DOCKER   := $(shell command -v docker)

# Files/paths
ENVSH   := $(CURDIR)/.devcontainer/scripts/env.sh
LIBSH   := $(CURDIR)/.devcontainer/scripts/lib.sh
K3D_CFG := $(CURDIR)/.devcontainer/k3d/k3d.yaml

# Targets
.PHONY: help cluster dashboard chart token delete

help:
	@echo ""
	@echo "Targets:"
	@echo ""
	@echo "  cluster     → create k3d cluster using config \"$(K3D_CFG)\""
	@echo "  dashboard   → install Kubernetes Dashboard and print login token"
	@echo "  token       → re-print Kubernetes Dashboard login token"
	@echo "  chart       → pull/unpack app chart (clobbers existing files)"
	@echo "                  - set APP_CHART_URL to override default \"oci://ghcr.io/$${ORG_NAME}/oci/$${APP_NAME}\""
	@echo "  delete      → delete all k3d clusters (local dev cleanup)"
	@echo ""
	@echo "Other devcontainer commands:"
	@echo ""
	@echo "  docker compose up                   → local dev"
	@echo "  skaffold dev                        → build + deploy to local cluster to verify deployment/helm release"
	@echo "  nix-shell -p {nixPackage}           → enter nix shell with specific package"
	@echo "  helm repo add {repoName} {repoURL}  → add a helm repository"
	@echo "  kubeconform|kubeval {file}          → validate Kubernetes YAML files"
	@echo ""

cluster:
	@. "$(ENVSH)"; . "$(LIBSH)"; \
	"$(CURDIR)/.devcontainer/scripts/cluster.sh"
	@. "$(ENVSH)"; . "$(LIBSH)"; \
	"$(CURDIR)/.devcontainer/scripts/app-chart.sh"

dashboard:
	@. "$(ENVSH)"; . "$(LIBSH)"; \
	"$(CURDIR)/.devcontainer/scripts/kubernetes-dashboard.sh"

chart:
	@. "$(ENVSH)"; . "$(LIBSH)"; \
	"$(CURDIR)/.devcontainer/scripts/app-chart.sh"

token:
	@. "$(ENVSH)" && \
	if [ -s "$$TOKEN_PATH" ]; then \
	  echo "Token file: $$TOKEN_PATH"; \
	  echo "---- TOKEN ----"; \
	  cat "$$TOKEN_PATH"; echo; \
	else \
	  echo "No token found. Run 'make dashboard' first."; \
	  exit 1; \
	fi

delete:
	@echo "❌ Deleting all k3d clusters..."
	@. "$(ENVSH)"; \
	if [ -z "$(K3D)" ]; then echo "k3d not found"; exit 127; fi; \
	$(K3D) cluster delete -a || true; \
	rm -f "$$TOKEN_PATH"
