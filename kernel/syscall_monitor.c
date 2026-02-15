// kernel/syscall_monitor.c
/*
 * System Call Monitoring Module
 * Detects suspicious system call patterns using kprobes
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
#include <linux/slab.h>
#include <linux/printk.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("OnePiece Team");
MODULE_DESCRIPTION("AMD Security Layer - System Call Monitor");
MODULE_VERSION("1.0.0");

// Suspicious syscall patterns
static unsigned long suspicious_syscalls = 0;
static unsigned long suspicious_patterns_detected = 0;

// Syscall statistics
typedef struct {
    unsigned long execve_count;
    unsigned long open_count;
    unsigned long write_count;
    unsigned long socket_count;
    unsigned long ptrace_count;
} syscall_stats_t;

static syscall_stats_t syscall_stats = {0};

/**
 * Kprobe handler for execve system call
 * Detects execution of suspicious binaries
 */
static int handler_execve(struct kprobe *p, struct pt_regs *regs)
{
    syscall_stats.execve_count++;
    
    // Check for suspicious execution patterns
    // (In real implementation, would check filename against threat database)
    
    return 0;
}

/**
 * Kprobe handler for file open operations
 */
static int handler_open(struct kprobe *p, struct pt_regs *regs)
{
    syscall_stats.open_count++;
    
    // Detect excessive file opens (potential brute force or data exfiltration)
    if (syscall_stats.open_count > 1000) {
        pr_warn("[AMD-SECURITY-SYSCALL] Excessive file open calls detected\n");
        suspicious_syscalls++;
    }
    
    return 0;
}

/**
 * Kprobe handler for write operations
 */
static int handler_write(struct kprobe *p, struct pt_regs *regs)
{
    syscall_stats.write_count++;
    return 0;
}

/**
 * Kprobe handler for socket operations
 * Detects potential C2 communication
 */
static int handler_socket(struct kprobe *p, struct pt_regs *regs)
{
    syscall_stats.socket_count++;
    
    // Rapid socket creation might indicate C2 or DDoS
    if (syscall_stats.socket_count > 100) {
        pr_warn("[AMD-SECURITY-SYSCALL] Suspicious socket creation pattern\n");
        suspicious_patterns_detected++;
    }
    
    return 0;
}

/**
 * Kprobe handler for ptrace (process tracing)
 * Used by debuggers but also by attackers
 */
static int handler_ptrace(struct kprobe *p, struct pt_regs *regs)
{
    syscall_stats.ptrace_count++;
    
    pr_warn("[AMD-SECURITY-SYSCALL] ptrace() call detected (PID: %d)\n", 
           current->pid);
    suspicious_patterns_detected++;
    
    return 0;
}

// Define kprobes for various syscalls
static struct kprobe kp[] = {
    {
        .symbol_name = "__x64_sys_execve",
        .pre_handler = handler_execve,
    },
    {
        .symbol_name = "__x64_sys_openat",
        .pre_handler = handler_open,
    },
    {
        .symbol_name = "__x64_sys_write",
        .pre_handler = handler_write,
    },
    {
        .symbol_name = "__x64_sys_socket",
        .pre_handler = handler_socket,
    },
    {
        .symbol_name = "__x64_sys_ptrace",
        .pre_handler = handler_ptrace,
    },
};

/**
 * Module initialization
 */
static int __init syscall_monitor_init(void)
{
    int ret;
    int i;
    
    pr_info("[AMD-SECURITY] Initializing Syscall Monitor Module\n");
    
    // Register kprobes
    for (i = 0; i < ARRAY_SIZE(kp); i++) {
        ret = register_kprobe(&kp[i]);
        if (ret < 0) {
            pr_err("[AMD-SECURITY] Failed to register kprobe for %s\n", 
                  kp[i].symbol_name);
            // Continue with other probes
        } else {
            pr_info("[AMD-SECURITY] Kprobe registered for %s\n", 
                   kp[i].symbol_name);
        }
    }
    
    pr_info("[AMD-SECURITY] Syscall Monitor loaded - monitoring suspicious patterns\n");
    return 0;
}

/**
 * Module cleanup
 */
static void __exit syscall_monitor_exit(void)
{
    int i;
    
    pr_info("[AMD-SECURITY] Unloading Syscall Monitor Module\n");
    
    // Unregister kprobes
    for (i = 0; i < ARRAY_SIZE(kp); i++) {
        unregister_kprobe(&kp[i]);
    }
    
    // Print statistics
    pr_info("[AMD-SECURITY-STATS] Syscall Statistics:\n");
    pr_info("[AMD-SECURITY-STATS]   execve: %lu\n", syscall_stats.execve_count);
    pr_info("[AMD-SECURITY-STATS]   open: %lu\n", syscall_stats.open_count);
    pr_info("[AMD-SECURITY-STATS]   write: %lu\n", syscall_stats.write_count);
    pr_info("[AMD-SECURITY-STATS]   socket: %lu\n", syscall_stats.socket_count);
    pr_info("[AMD-SECURITY-STATS]   ptrace: %lu\n", syscall_stats.ptrace_count);
    pr_info("[AMD-SECURITY-STATS]   Suspicious syscalls: %lu\n", suspicious_syscalls);
    pr_info("[AMD-SECURITY-STATS]   Suspicious patterns: %lu\n", 
           suspicious_patterns_detected);
}

module_init(syscall_monitor_init);
module_exit(syscall_monitor_exit);
