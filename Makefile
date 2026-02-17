# Makefile for Luminol AUR packaging

# Variables are derived from the PKGBUILD file
PKGBUILD_VERSION := $(shell grep -m 1 "pkgver=" PKGBUILD | cut -d '=' -f 2)
REPO_NAME        := $(shell grep -m 1 "_pkgname=" PKGBUILD | cut -d '=' -f 2)
ARCHIVE_NAME     := ${REPO_NAME}-${PKGBUILD_VERSION}.tar.gz

.PHONY: all tar local-build publish clean help

all: help

help:
	@echo "Luminol AUR Packaging Helper"
	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  tar           Creates a local source tarball from the current git HEAD."
	@echo "  local-build   Builds the package from the local tarball for testing."
	@echo "                (NOTE: Your PKGBUILD 'source' must be set to the local file.)"
	@echo "  publish       Prepares final PKGBUILD and .SRCINFO for publishing."
	@echo "                (NOTE: Your PKGBUILD 'source' must be set to the remote URL.)"
	@echo "  clean         Removes all generated packaging artifacts."
	@echo ""

# --- Automation Targets ---

tar:
	@echo "--> Creating source archive: ${ARCHIVE_NAME}"
	@git archive --format=tar.gz --prefix=${REPO_NAME}-${PKGBUILD_VERSION}/ -o ${ARCHIVE_NAME} HEAD

local-build: tar
	@echo "--> Building package for local testing..."
	@updpkgsums
	@echo "--> Running makepkg..."
	@makepkg -si

publish:
	@echo "--> Preparing package for publishing to the AUR..."
	@updpkgsums
	@echo "--> Generating .SRCINFO file..."
	@makepkg --printsrcinfo > .SRCINFO
	@echo "--> Done. Ready to commit PKGBUILD and .SRCINFO to the AUR repository."

clean:
	@echo "--> Cleaning up generated files..."
	@rm -f *.tar.gz *.pkg.tar.zst
	@rm -rf pkg/ src/
	@echo "--> Done."
