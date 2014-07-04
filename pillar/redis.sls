redis:
  lookup:
    install_from: source
    home: /var/lib/redis
    user: redis
    port: 6379
    svc_state: stopped
    cfg_name: /etc/redis.conf
    pkg_name: redis
    svc_name: redis
    version: 2.8.12
    bind: 0.0.0.0
    databases: 8
    snapshots:
      - '600 100'
      - '300 1000'
      - '30 10000'

