
pg_hba.conf:
    file.managed:
        - name: /etc/postgresql/9.3/main/pg_hba.conf
        - source: salt://postgresql/pg_hba.conf
        - user: postgres
        - group: postgres
        - mode: 644



postgres-pkgs:
  pkg:
    - installed
    - pkgs:
      - postgresql-9.3
      - postgresql-contrib-9.3
      - postgresql-plpython-9.3
      - postgresql-server-dev-9.3

postgres_repo:
  pkgrepo.managed:
    - name: "deb http://apt.postgresql.org/pub/repos/apt/ {{ grains['oscodename'] }}-pgdg main"
    - file: /etc/apt/sources.list.d/pgdg.list
    - key_url: http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc
    - require_in:
        - pkg: postgres-pkgs


Postgres User:
    postgres_user.present:
        - name: {{ pillar['dbuser'] }}
        - password: {{ pillar['dbpassword'] }}
        - runas: postgres

Postgres DB:
    postgres_database.present:
        - name: {{ pillar['dbname'] }}
        - owner: {{ pillar['dbuser'] }}

