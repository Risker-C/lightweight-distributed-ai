# 最小匿名权限：允许基本可观测，不允许写操作

namespace "*" {
  policy = "read"
}

agent {
  policy = "read"
}

node {
  policy = "read"
}
