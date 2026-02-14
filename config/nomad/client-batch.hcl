# =====================
# Nomad Client - Batch Pool
# File: client-batch.hcl
# =====================

region     = "global"
datacenter = "dc1"
name       = "CHANGE_ME_BATCH_CLIENT_NAME"

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
  node_class = "batch"

  servers = [
    "10.10.10.11:4647",
    "10.10.10.12:4647",
    "10.10.10.13:4647"
  ]

  network_interface = "eth0"

  # 资源池标签（供批处理任务约束）
  meta {
    pool            = "batch"
    workload_type   = "batch"
    scheduling_tier = "silver"
  }

  # Batch 节点预留更少系统资源，提高可用算力
  reserved {
    cpu            = 300
    memory         = 512
    disk           = 1024
    reserved_ports = "22"
  }

  options {
    "driver.raw_exec.enable" = "0"
    "docker.cleanup.image"   = "true"
  }

  # 批处理场景更激进回收策略
  gc_interval              = "30s"
  gc_disk_usage_threshold  = 75
  gc_inode_usage_threshold = 65
  max_kill_timeout         = "10m"
}

acl {
  enabled = true
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
