# =====================
# Nomad Server (3-Node HA)
# File: server.hcl
# =====================

region     = "global"
datacenter = "dc1"
name       = "CHANGE_ME_SERVER_NAME"

log_level            = "INFO"
log_json             = true
disable_update_check = true
enable_syslog        = true
leave_on_terminate   = true

bind_addr  = "0.0.0.0"
data_dir   = "/opt/nomad"
plugin_dir = "/opt/nomad/plugins"

# 调整为实际网卡，例如 eth0 / ens192
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

server {
  enabled          = true
  bootstrap_expect = 3
  raft_protocol    = 3

  # 节点重启后自动重新加入 Raft 集群
  rejoin_after_leave = true

  # Server 发现与重试（恢复策略）
  server_join {
    retry_join = [
      "10.10.10.11:4648",
      "10.10.10.12:4648",
      "10.10.10.13:4648"
    ]
    retry_interval = "15s"
  }
}

acl {
  enabled = true

  # 降低 token/policy 缓存时间，提升权限变更生效速度
  token_ttl  = "30s"
  policy_ttl = "30s"
  role_ttl   = "30s"
}

tls {
  http = true
  rpc  = true

  verify_server_hostname = true
  verify_https_client    = true

  ca_file   = "/etc/nomad.d/tls/nomad-agent-ca.pem"
  cert_file = "/etc/nomad.d/tls/server.pem"
  key_file  = "/etc/nomad.d/tls/server-key.pem"
}

telemetry {
  publish_allocation_metrics = true
  publish_node_metrics       = true
}
