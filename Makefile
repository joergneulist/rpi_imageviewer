BUILDROOT_VERSION=buildroot-2025.11.1
CODE_TARGET_PATH=/opt/imvi
CONFIG_TARGET_PATH=/etc

BUILDROOT_FILE=$(BUILDROOT_VERSION).tar.xz
BUILDROOT_SOURCE=https://buildroot.org/downloads/$(BUILDROOT_FILE)
BUILDROOT_TARGET=out/br

PATCHES_DIR=buildroot_tailoring

DIR_SYSTEM_OVERLAY=out/system

CODE = $(wildcard src/*.py)
CODE_PATH = $(DIR_SYSTEM_OVERLAY)/$(CODE_TARGET_PATH)
CODE_TARGETS = $(patsubst src/%,$(CODE_PATH)/%, $(CODE))

CONFIG = $(wildcard etc/*)
CONFIG_PATH = $(DIR_SYSTEM_OVERLAY)/$(CONFIG_TARGET_PATH)
CONFIG_TARGETS = $(patsubst etc/%,$(CONFIG_PATH)/%, $(CONFIG))

.NOTINTERMEDIATE: cache/$(BUILDROOT_FILE)

.PHONY: all buildroot system_overlay clean

all: buildroot system_overlay clean clean_cache clean_out

buildroot: $(BUILDROOT_TARGET)

system_overlay: $(CODE_TARGETS) $(CONFIG_TARGETS)

clean: clean_cache clean_out

clean_cache:
	rm -rf cache

clean_out:
	rm -rf out


### LOAD AND UNZIP BUILDROOT

cache/$(BUILDROOT_FILE):
	mkdir -p $@$(dir $@)
	wget -O $@ $(BUILDROOT_SOURCE)

$(BUILDROOT_TARGET): cache/$(BUILDROOT_FILE)
	mkdir -p $(dir $@)
	tar xf $<
	mv $(BUILDROOT_VERSION) $@


### BUILDROOT CONFIGURATION



### CREATE SYSTEM OVERLAY

$(CODE_TARGETS): $(CODE_PATH)/%: src/%
	mkdir -p $(dir $@)
	cp $< $@

$(CONFIG_TARGETS): $(CONFIG_PATH)/%: etc/%
	mkdir -p $(dir $@)
	cp $< $@
