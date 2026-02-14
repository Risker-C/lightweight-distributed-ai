# =====================
# Nomad Client - Warm Pool
# File: client-warm.hcl
# =====================

region     = "global"
datacenter = "dc1"
name       = "CHANGE_ME_WARM_CLIENT_NAME"

log_level            = "INFO"
log_json             = true
disable_update_check = true
enable_syslog        = true
leave_on_terminate   = true

bind_addr  = "0.0.0.0"
data_dir   = "/opt/nomad"
plugin_dir = "/opt/nomad/plugins"

advertise {
  http = "{{ GetInterfaceIP \"eth0\" }}:4646"
  rpc  = "{{ GetInterfaceIP \"eth0\" }}:4647"
  serf = "{{ GetInterfaceIP \"eth0\" }}:4648"
}

addresses {
  http = "0.0.0.0"
  rpc  = "0.0.0.0"
  serf = "0.0.0.0"
}

ports {
  http = 4646
  rpc  = 4647
  serf = 4648
}

client {
  enabled    = true
  node_class = "warm"

  # Nomad Server RPC 地址（调度控制面）
  servers = [
    "10.10.10.11:4647",
    "10.10.10.12:4647",
    "10.10.10.13:4647"
  ]

  network_interface = "eth0"

  # 资源池标签（供调度约束/亲和性使用）
  meta {
    pool            = "warm"
    workload_type   = "service"
    scheduling_tier = "gold"
  }

  # 为系统守护进程预留资源
  reserved {
    cpu            = 500
    memory         = 1024
    disk           = 2048
    reserved_ports = "22"
  }

  options {
    "driver.raw_exec.enable" = "0"
    "docker.cleanup.image"   = "true"
  }

  # 恢复策略
  gc_interval              = "1m"
  gc_disk_usage_threshold  = 80
  gc_inode_usage_threshold = 70
  max_kill_timeout         = "30m"
}

acl {
  enabled = true
  # 建议注入 Agent Token（权限最小化）
  # token = "REPLACE_WITH_CLIENT_AGENT_TOKEN"
}

tls {
  http = true
  rpc  = true

  verify_server_hostname = true
  verify_https_client    = true

  ca_file   = "/etc/nomad.d/tls/nomad-agent-ca.pem"
  cert_file = "/etc/nomad.d/tls/client.pem"
  key_file  = "/etc/nomad.d/tls/client-key.pem"
}
