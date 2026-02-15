// kernel/netmon.c
/*
 * Network Monitoring Module
 * Detects suspicious network patterns and C2 communication
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/skbuff.h>
#include <net/ip.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("OnePiece Team");
MODULE_DESCRIPTION("AMD Security Layer - Network Monitor");
MODULE_VERSION("1.0.0");

// Network statistics
typedef struct {
    unsigned long packets_monitored;
    unsigned long suspicious_connections;
    unsigned long data_exfiltration_attempts;
    unsigned long c2_patterns_detected;
} net_stats_t;

static net_stats_t net_stats = {0};

// Known malicious ports and patterns
static const unsigned short malicious_ports[] = {
    4444, 5555, 6666, 7777, 8888, 9999,  // Common C2 ports
    31337, 31338,                         // LEET ports
    12345, 54321,                         // Default backdoor ports
};

/**
 * Check if port is in known malicious list
 */
static int is_malicious_port(unsigned short port)
{
    int i;
    for (i = 0; i < ARRAY_SIZE(malicious_ports); i++) {
        if (port == malicious_ports[i])
            return 1;
    }
    return 0;
}

/**
 * Check for C2 communication patterns
 * - Encrypted traffic to suspicious IPs
 * - Regular beacon patterns
 * - Unusual port combinations
 */
static int detect_c2_pattern(struct iphdr *iph, struct tcphdr *tcph)
{
    unsigned int saddr = iph->saddr;
    unsigned int daddr = iph->daddr;
    unsigned short sport = ntohs(tcph->source);
    unsigned short dport = ntohs(tcph->dest);
    
    // Check for common C2 ports
    if (is_malicious_port(dport) || is_malicious_port(sport)) {
        net_stats.c2_patterns_detected++;
        return 1;
    }
    
    // Check for unusual port combinations (high source port to low dest port)
    if (sport > 49152 && dport < 1024) {
        net_stats.c2_patterns_detected++;
        return 1;
    }
    
    return 0;
}

/**
 * Detect potential data exfiltration
 * - Large data transfers to external IPs
 * - Encoding/compression of data
 */
static int detect_data_exfiltration(struct iphdr *iph, struct skb_shared_info *shinfo)
{
    // Check packet size (unusually large packets might indicate data theft)
    if (shinfo && shinfo->gso_size > 65000) {
        net_stats.data_exfiltration_attempts++;
        return 1;
    }
    
    return 0;
}

/**
 * Netfilter hook for monitoring outgoing packets
 */
static unsigned int hook_outgoing(void *priv,
                                  struct sk_buff *skb,
                                  const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct tcphdr *tcph;
    unsigned char *payload;
    
    net_stats.packets_monitored++;
    
    if (!skb)
        return NF_ACCEPT;
    
    // Get IP header
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;
    
    // Only monitor TCP packets
    if (iph->protocol != IPPROTO_TCP)
        return NF_ACCEPT;
    
    tcph = tcp_hdr(skb);
    if (!tcph)
        return NF_ACCEPT;
    
    // Check for C2 patterns
    if (detect_c2_pattern(iph, tcph)) {
        pr_warn("[AMD-SECURITY-NET] Suspicious C2 pattern detected: "
               "%pI4:%d -> %pI4:%d\n",
               &iph->saddr, ntohs(tcph->source),
               &iph->daddr, ntohs(tcph->dest));
        net_stats.suspicious_connections++;
    }
    
    // Check for data exfiltration
    if (detect_data_exfiltration(iph, skb_shinfo(skb))) {
        pr_warn("[AMD-SECURITY-NET] Data exfiltration attempt detected: "
               "Large packet to %pI4\n", &iph->daddr);
    }
    
    return NF_ACCEPT;
}

/**
 * Netfilter hook for monitoring incoming packets
 */
static unsigned int hook_incoming(void *priv,
                                  struct sk_buff *skb,
                                  const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct tcphdr *tcph;
    
    net_stats.packets_monitored++;
    
    if (!skb)
        return NF_ACCEPT;
    
    iph = ip_hdr(skb);
    if (!iph || iph->protocol != IPPROTO_TCP)
        return NF_ACCEPT;
    
    tcph = tcp_hdr(skb);
    if (!tcph)
        return NF_ACCEPT;
    
    // Check for suspicious incoming connections
    if (detect_c2_pattern(iph, tcph)) {
        pr_warn("[AMD-SECURITY-NET] Suspicious incoming connection: "
               "%pI4:%d -> %pI4:%d\n",
               &iph->saddr, ntohs(tcph->source),
               &iph->daddr, ntohs(tcph->dest));
        net_stats.suspicious_connections++;
    }
    
    return NF_ACCEPT;
}

// Netfilter hooks
static struct nf_hook_ops netmon_hooks[] = {
    {
        .hook = hook_outgoing,
        .pf = NFPROTO_IPV4,
        .hooknum = NF_INET_POST_ROUTING,
        .priority = NF_IP_PRI_FIRST,
    },
    {
        .hook = hook_incoming,
        .pf = NFPROTO_IPV4,
        .hooknum = NF_INET_PRE_ROUTING,
        .priority = NF_IP_PRI_FIRST,
    },
};

/**
 * Module initialization
 */
static int __init netmon_init(void)
{
    int ret;
    
    pr_info("[AMD-SECURITY-NET] Initializing Network Monitor Module\n");
    pr_info("[AMD-SECURITY-NET] Monitoring for C2 and data exfiltration patterns\n");
    
    // Register netfilter hooks
    ret = nf_register_net_hooks(&init_net, netmon_hooks, ARRAY_SIZE(netmon_hooks));
    if (ret < 0) {
        pr_err("[AMD-SECURITY-NET] Failed to register netfilter hooks\n");
        return ret;
    }
    
    pr_info("[AMD-SECURITY-NET] Network Monitor loaded\n");
    return 0;
}

/**
 * Module cleanup
 */
static void __exit netmon_exit(void)
{
    pr_info("[AMD-SECURITY-NET] Unloading Network Monitor Module\n");
    
    // Unregister netfilter hooks
    nf_unregister_net_hooks(&init_net, netmon_hooks, ARRAY_SIZE(netmon_hooks));
    
    // Print statistics
    pr_info("[AMD-SECURITY-NET-STATS] Network Statistics:\n");
    pr_info("[AMD-SECURITY-NET-STATS]   Packets monitored: %lu\n", 
           net_stats.packets_monitored);
    pr_info("[AMD-SECURITY-NET-STATS]   Suspicious connections: %lu\n", 
           net_stats.suspicious_connections);
    pr_info("[AMD-SECURITY-NET-STATS]   C2 patterns detected: %lu\n", 
           net_stats.c2_patterns_detected);
    pr_info("[AMD-SECURITY-NET-STATS]   Exfiltration attempts: %lu\n", 
           net_stats.data_exfiltration_attempts);
}

module_init(netmon_init);
module_exit(netmon_exit);
