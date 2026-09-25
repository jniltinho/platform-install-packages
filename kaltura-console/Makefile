VERSION ?= $(shell git describe --tags --match 'kaltura-console/v*' --dirty 2>/dev/null | sed 's|^kaltura-console/v||' || true)
ifeq ($(strip $(VERSION)),)
VERSION := 0.1.0-dev
endif
COMMIT := $(shell git rev-parse --short HEAD)
BUILD_DATE := $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
LDFLAGS := -s -w -X kaltura-console/internal/buildinfo.Version=$(VERSION) -X kaltura-console/internal/buildinfo.GitCommit=$(COMMIT) -X kaltura-console/internal/buildinfo.BuildDate=$(BUILD_DATE)
.PHONY: frontend build test lint package
frontend:
	cd frontend && npm ci && npm run build
	touch web/dist/.gitkeep
build: frontend
	mkdir -p bin
	CGO_ENABLED=0 go build -trimpath -ldflags '$(LDFLAGS)' -o bin/kaltura-console .
test:
	CGO_ENABLED=0 go test ./...
	go test -race ./...
	cd frontend && npm test
lint:
	golangci-lint run ./...
	cd frontend && npm run lint
	cmp config.toml.example internal/config/example.toml
package: build
	mkdir -p dist
	VERSION='$(VERSION)' ARCH=amd64 nfpm package --config packaging/nfpm.yaml --packager deb --target dist/
	VERSION='$(VERSION)' ARCH=amd64 nfpm package --config packaging/nfpm.yaml --packager rpm --target dist/
	tar -czf dist/kaltura-console_$(VERSION)_linux_amd64.tar.gz -C bin kaltura-console -C .. config.toml.example README.md CHANGELOG.md
	cd dist && sha256sum *.deb *.rpm *.tar.gz > SHA256SUMS
