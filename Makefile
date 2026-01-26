# GENERAL SETTINGS
# Inspect and modify these variables to suit your needs

# buildroot-2025.11.1 was tested and works; if you upgrade, expect hiccups
BUILDROOT_VERSION=buildroot-2025.11.1

# This is the base config for your target; I was using a raspberry pi 1B
BUILDROOT_BASE_CONFIG=$(HOST_PATH_BUILDROOT)/configs/raspberrypi_defconfig

# Paths inside the target filesystem
TARGET_EXECUTABLE=/usr/bin/imvi
TARGET_PATH_PYTHON=/opt/imvi
TARGET_PATH_CONFIG=/etc
TARGET_PATH_ASSETS=/opt/imvi/assets

# Target image configuration
TARGET_HOSTNAME=imvi
TARGET_GREETING=Welcome to IMVI!
TARGET_ROOT_PASSWORD=imvi

# BUILD SETTINGS
# This affects the internal behaviour; you shouldn't need to modify these

BUILDROOT_FINAL_CONFIG_NAME=raspberrypi_imvi_defconfig
HOST_PATH_BUILD=out
HOST_PATH_CACHE=cache
HOST_PATH_BUILDROOT=$(HOST_PATH_BUILD)/br
HOST_PATH_SYSTEM_OVERLAY=$(HOST_PATH_BUILD)/system

HOST_CONFIG_PATCH=$(HOST_PATH_BUILD)/br_config_patch

BUILDROOT_FINAL_CONFIG_FILE=$(HOST_PATH_BUILDROOT)/configs/$(BUILDROOT_FINAL_CONFIG_NAME)


# MAKEFILE INTERNALS & SOURCES
# Better not touch

SOURCE_ENTRY_POINT = main.py
SOURCE_PYTHON = $(wildcard src/*.py)
SOURCE_CONFIG = $(wildcard etc/*/*)
SOURCE_ASSETS = $(wildcard assets/*.png)
SOURCE_BUILDROOT = buildroot_tailoring
SOURCE_BR_CONFIG_PATCH = $(SOURCE_BUILDROOT)/configs/config_patch
SOURCE_BR_BOARD = $(SOURCE_BUILDROOT)/board
TARGET_OVERLAY_PYTHON=$(patsubst src/%,$(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_PYTHON)/%, $(SOURCE_PYTHON))
TARGET_OVERLAY_CONFIG=$(patsubst etc/%,$(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_CONFIG)/%, $(SOURCE_CONFIG))
TARGET_OVERLAY_BIN=$(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_EXECUTABLE)
TARGET_OVERLAY_ASSETS=$(patsubst assets/%,$(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_ASSETS)/%, $(SOURCE_ASSETS))

###############################################################################

### HIGH LEVEL TARGETS

.PHONY: all buildroot system_overlay compile clean clean_all clean_cache

all: compile

buildroot: $(BUILDROOT_FINAL_CONFIG_FILE)

system_overlay: $(TARGET_OVERLAY_PYTHON) $(TARGET_OVERLAY_CONFIG) $(TARGET_OVERLAY_BIN) $(TARGET_OVERLAY_ASSETS)

compile: $(HOST_PATH_BUILD)/sdcard.img

clean:
	rm -rf $(HOST_PATH_BUILD)

clean_cache:
	rm -rf $(HOST_PATH_CACHE)

clean_all: clean clean_cache


### LOAD AND UNZIP BUILDROOT

BUILDROOT_FILE=$(BUILDROOT_VERSION).tar.xz
BUILDROOT_SOURCE=https://buildroot.org/downloads/$(BUILDROOT_FILE)
BUILDROOT_CACHE=$(HOST_PATH_CACHE)/$(BUILDROOT_FILE)

.NOTINTERMEDIATE: $(BUILDROOT_CACHE)

$(BUILDROOT_CACHE):
	mkdir -p $@$(dir $@)
	wget -O $@ $(BUILDROOT_SOURCE)

$(HOST_PATH_BUILDROOT): $(BUILDROOT_CACHE)
	mkdir -p $(dir $@)
	tar xf $<
	mv $(BUILDROOT_VERSION) $@

$(BUILDROOT_BASE_CONFIG): $(HOST_PATH_BUILDROOT)


### BUILDROOT CONFIGURATION

SED_RULE_1 = 's,++BOARD-PATH++,$(shell readlink -f $(SOURCE_BR_BOARD)),g'
SED_RULE_2 = 's,++SYSTEM-PATH++,$(shell readlink -f $(HOST_PATH_SYSTEM_OVERLAY)),g'
SED_RULE_3 = 's,++HOSTNAME++,$(TARGET_HOSTNAME),g'
SED_RULE_4 = 's,++GREETING++,$(TARGET_GREETING),g'
SED_RULE_5 = 's,++ROOT-PASSWORD++,$(TARGET_ROOT_PASSWORD),g'
SED_RULE_6 = 's,++IMVI_PATH++,$(TARGET_PATH_PYTHON),g'
$(HOST_CONFIG_PATCH): $(SOURCE_BR_CONFIG_PATCH)
	mkdir -p $(dir $@)
	sed -e $(SED_RULE_1) -e $(SED_RULE_2) -e $(SED_RULE_3) -e $(SED_RULE_4) -e $(SED_RULE_5) -e $(SED_RULE_6) $< >$@

AWK_RULE = '{a[$$1]=$$0} END{for(x in a)print a[x]}'
$(BUILDROOT_FINAL_CONFIG_FILE): $(BUILDROOT_BASE_CONFIG) $(HOST_CONFIG_PATCH)
	awk -F= $(AWK_RULE) $^>$@


### CREATE SYSTEM OVERLAY

$(TARGET_OVERLAY_PYTHON): $(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_PYTHON)/%: src/%
	mkdir -p $(dir $@)
	cp $< $@

$(TARGET_OVERLAY_CONFIG): $(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_CONFIG)/%: etc/%
	mkdir -p $(dir $@)
	cp $< $@

$(TARGET_OVERLAY_BIN):
	mkdir -p $(dir $@)
	ln -fs $(TARGET_PATH_PYTHON)/$(SOURCE_ENTRY_POINT) $@

$(TARGET_OVERLAY_ASSETS): $(HOST_PATH_SYSTEM_OVERLAY)$(TARGET_PATH_ASSETS)/%: assets/%
	mkdir -p $(dir $@)
	cp $< $@


### COMPILATION

$(HOST_PATH_BUILDROOT)/.config: $(BUILDROOT_FINAL_CONFIG_FILE)
	$(MAKE) -C $(HOST_PATH_BUILDROOT) $(BUILDROOT_FINAL_CONFIG_NAME)

$(HOST_PATH_BUILDROOT)/output/images/sdcard.img: $(HOST_PATH_BUILDROOT)/.config $(TARGET_OVERLAY_PYTHON) $(TARGET_OVERLAY_CONFIG) $(TARGET_OVERLAY_BIN) $(TARGET_OVERLAY_ASSETS)
	$(MAKE) -C $(HOST_PATH_BUILDROOT)

$(HOST_PATH_BUILD)/sdcard.img: $(HOST_PATH_BUILDROOT)/output/images/sdcard.img
	cp $< $@
