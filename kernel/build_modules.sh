// kernel/build_modules.sh
#!/bin/bash
# Comprehensive build and installation script for AMD Security Layer Kernel Modules

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        print_warning "Run with: sudo $0"
        exit 1
    fi
    print_success "Running as root"
}

# Check kernel version
check_kernel() {
    print_header "Checking Kernel Compatibility"
    
    KERNEL_VERSION=$(uname -r)
    KERNEL_MAJOR=$(echo $KERNEL_VERSION | cut -d. -f1)
    KERNEL_MINOR=$(echo $KERNEL_VERSION | cut -d. -f2)
    
    echo -e "${BLUE}Kernel Version: $KERNEL_VERSION${NC}"
    
    # Require Linux 5.0+
    if [ "$KERNEL_MAJOR" -lt 5 ]; then
        print_error "Kernel version 5.0+ required (you have $KERNEL_VERSION)"
        exit 1
    fi
    
    print_success "Kernel version compatible"
}

# Check build tools
check_build_tools() {
    print_header "Checking Build Tools"
    
    # Check for gcc
    if ! command -v gcc &> /dev/null; then
        print_error "gcc not found"
        print_warning "Install with: sudo apt-get install build-essential"
        exit 1
    fi
    print_success "gcc found: $(gcc --version | head -1)"
    
    # Check for make
    if ! command -v make &> /dev/null; then
        print_error "make not found"
        exit 1
    fi
    print_success "make found: $(make --version | head -1)"
    
    # Check for kernel headers
    if [ ! -d "/lib/modules/$KERNEL_VERSION/build" ]; then
        print_error "Kernel headers not found"
        print_warning "Install with: sudo apt-get install linux-headers-$KERNEL_VERSION"
        exit 1
    fi
    print_success "Kernel headers found"
}

# Build LSM module
build_lsm_module() {
    print_header "Building AMD Security LSM Module"
    
    cd "$(dirname "$0")"
    
    print_warning "Building amd_security_lsm.ko..."
    make clean
    make
    
    if [ -f "amd_security_lsm.ko" ]; then
        print_success "amd_security_lsm.ko built successfully"
        ls -lh amd_security_lsm.ko
    else
        print_error "Failed to build amd_security_lsm.ko"
        exit 1
    fi
}

# Build syscall monitor module
build_syscall_monitor() {
    print_header "Building Syscall Monitor Module"
    
    print_warning "Compiling syscall_monitor.c..."
    
    KERNEL_BUILD=/lib/modules/$(uname -r)/build
    
    gcc -c syscall_monitor.c \
        -I$KERNEL_BUILD/include \
        -I$KERNEL_BUILD/arch/x86/include \
        -D__KERNEL__ \
        -DMODULE \
        -O2 \
        -Wall \
        -Werror
    
    # Link with kernel module
    ld -r -o syscall_monitor.ko syscall_monitor.o
    
    if [ -f "syscall_monitor.ko" ]; then
        print_success "syscall_monitor.ko built successfully"
        ls -lh syscall_monitor.ko
    else
        print_error "Failed to build syscall_monitor.ko"
        exit 1
    fi
}

# Build network monitor module
build_netmon() {
    print_header "Building Network Monitor Module"
    
    print_warning "Compiling netmon.c..."
    
    KERNEL_BUILD=/lib/modules/$(uname -r)/build
    
    gcc -c netmon.c \
        -I$KERNEL_BUILD/include \
        -I$KERNEL_BUILD/arch/x86/include \
        -D__KERNEL__ \
        -DMODULE \
        -O2 \
        -Wall \
        -Werror
    
    # Link with kernel module
    ld -r -o netmon.ko netmon.o
    
    if [ -f "netmon.ko" ]; then
        print_success "netmon.ko built successfully"
        ls -lh netmon.ko
    else
        print_error "Failed to build netmon.ko"
        exit 1
    fi
}

# Install modules
install_modules() {
    print_header "Installing Kernel Modules"
    
    MODULES_DIR="/lib/modules/$(uname -r)/kernel/security"
    
    # Create directory if doesn't exist
    mkdir -p "$MODULES_DIR"
    
    # Copy modules
    if [ -f "amd_security_lsm.ko" ]; then
        cp amd_security_lsm.ko "$MODULES_DIR/"
        print_success "Installed amd_security_lsm.ko"
    fi
    
    if [ -f "syscall_monitor.ko" ]; then
        cp syscall_monitor.ko "$MODULES_DIR/"
        print_success "Installed syscall_monitor.ko"
    fi
    
    if [ -f "netmon.ko" ]; then
        cp netmon.ko "$MODULES_DIR/"
        print_success "Installed netmon.ko"
    fi
    
    # Update module dependencies
    depmod -a
    print_success "Module dependencies updated"
}

# Load modules
load_modules() {
    print_header "Loading Kernel Modules"
    
    # Load main LSM module
    if modprobe amd_security_lsm threat_threshold=70; then
        print_success "Loaded amd_security_lsm"
    else
        print_warning "Could not load amd_security_lsm (may require newer kernel)"
    fi
    
    # Load syscall monitor
    if modprobe syscall_monitor; then
        print_success "Loaded syscall_monitor"
    else
        print_warning "Could not load syscall_monitor"
    fi
    
    # Load network monitor
    if modprobe netmon; then
        print_success "Loaded netmon"
    else
        print_warning "Could not load netmon"
    fi
}

# Show module status
show_status() {
    print_header "Loaded Kernel Modules"
    
    echo -e "${BLUE}Module Status:${NC}"
    lsmod | grep amd_security || echo "  No AMD Security modules loaded"
    
    print_header "Kernel Logs"
    echo -e "${BLUE}Recent messages:${NC}"
    dmesg | grep "AMD-SECURITY" | tail -20 || echo "  No AMD Security messages yet"
    
    print_header "Module Statistics"
    if [ -f "/proc/amd_security/stats" ]; then
        cat /proc/amd_security/stats
    else
        echo "  Statistics file not available yet"
    fi
}

# Main execution
main() {
    print_header "AMD Ryzen AI Security Layer - Kernel Module Builder"
    
    # Parse command line arguments
    case "${1:-build}" in
        build)
            check_root
            check_kernel
            check_build_tools
            build_lsm_module
            ;;
        install)
            check_root
            check_kernel
            install_modules
            load_modules
            show_status
            ;;
        full)
            check_root
            check_kernel
            check_build_tools
            build_lsm_module
            install_modules
            load_modules
            show_status
            ;;
        status)
            show_status
            ;;
        clean)
            print_header "Cleaning Build Artifacts"
            make clean
            rm -f *.ko *.o *.mod.c *.mod.o
            print_success "Cleanup complete"
            ;;
        unload)
            check_root
            print_header "Unloading Kernel Modules"
            modprobe -r amd_security_lsm 2>/dev/null || print_warning "Module not loaded"
            modprobe -r syscall_monitor 2>/dev/null || print_warning "Module not loaded"
            modprobe -r netmon 2>/dev/null || print_warning "Module not loaded"
            print_success "Modules unloaded"
            ;;
        *)
            echo "Usage: $0 {build|install|full|status|clean|unload}"
            echo ""
            echo "Commands:"
            echo "  build   - Compile kernel modules (default)"
            echo "  install - Compile and install modules"
            echo "  full    - Complete build and installation"
            echo "  status  - Show module status and statistics"
            echo "  clean   - Remove build artifacts"
            echo "  unload  - Unload modules from kernel"
            exit 1
            ;;
    esac
}

main "$@"
