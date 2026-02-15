# kernel/Makefile
# Linux Kernel Module Build Configuration

# Kernel module name
obj-m += amd_security_lsm.o

# Kernel build directory (modify based on your kernel)
KDIR ?= /lib/modules/$(shell uname -r)/build

# Current directory
PWD := $(shell pwd)

# Build flags
EXTRA_CFLAGS := -Wall -Werror -Wno-unused-parameter \
                -march=native -O2

# Default target
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Clean build artifacts
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

# Install module (requires root)
install: all
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

# Uninstall module (requires root)
uninstall:
	modprobe -r amd_security_lsm
	rm -f /lib/modules/$(shell uname -r)/kernel/security/amd_security_lsm.ko

# Load module (requires root)
load: install
	modprobe amd_security_lsm threat_threshold=70

# Unload module (requires root)
unload:
	modprobe -r amd_security_lsm

# View module logs
logs:
	dmesg | grep AMD-SECURITY

# View statistics
stats:
	cat /proc/amd_security/stats

# Monitor in real-time
monitor:
	@echo "Monitoring AMD Security Layer..."
	@while true; do \
		clear; \
		echo "=== AMD Security Layer Kernel Module ==="; \
		echo "Time: $$(date)"; \
		echo ""; \
		cat /proc/amd_security/stats; \
		echo ""; \
		echo "Recent kernel messages:"; \
		dmesg | grep AMD-SECURITY | tail -5; \
		sleep 2; \
	done

# Compile and verify
check: clean all
	@echo "Checking module compilation..."
	@file amd_security_lsm.ko

.PHONY: all clean install uninstall load unload logs stats monitor check
