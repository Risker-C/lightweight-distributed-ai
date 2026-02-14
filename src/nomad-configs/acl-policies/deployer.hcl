# 应用发布角色（CI/CD 使用）

namespace "*" {
  policy = "write"

  capabilities = [
    "alloc-exec",
    "alloc-lifecycle",
    "csi-read-volume",
    "csi-write-volume",
    "dispatch-job",
    "list-jobs",
    "parse-job",
    "read-fs",
    "read-job",
    "read-logs",
    "submit-job"
  ]
}

agent {
  policy = "read"
}

node {
  policy = "read"
}

operator {
  policy = "read"
}
