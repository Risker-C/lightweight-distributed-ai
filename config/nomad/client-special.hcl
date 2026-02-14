# =====================
# Nomad Client - Special Pool
# File: client-special.hcl
# 说明：满足 warm/batch/special 三资源池需求
# =====================

region     = "global"
datacenter = "dc1"
name       = "CHANGE_ME_SPECIAL_CLIENT_NAME"

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
  node_class = "special"

  servers = [
    "10.10.10.11:4647",
    "10.10.10.12:4647",
    "10.10.10.13:4647"
  ]

  network_interface = "eth0"

  # 高优先级/关键业务池
  meta {
    pool            = "special"
    workload_type   = "critical"
    scheduling_tier = "platinum"
  }

  reserved {
    cpu            = 700
    memory         = 2048
    disk           = 4096
    reserved_ports = "22"
  }

  options {
    "driver.raw_exec.enable" = "0"
    "docker.cleanup.image"   = "true"
  }

  gc_interval              = "2m"
  gc_disk_usage_threshold  = 85
  gc_inode_usage_threshold = 75
  max_kill_timeout         = "45m"
}

acl {
  enabled = true
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
