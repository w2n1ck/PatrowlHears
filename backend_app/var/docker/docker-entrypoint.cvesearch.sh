#!/bin/bash
# Small script to control container behavior.

cd $CVE_BASE

function show_help {
  printf "Used to launch CVE database.\n \
          \t-h|--help: this help menu\n\
          \t-i|--initialize: initialize database for the first time\n\
          \t-u|--update: update database\n\
          \t-r|--repopulate: repopulate database\n"
}

function log {
  echo "==================== $1 ===================="
}

function update_repo {
  log "Updating repo"
  curl -sL https://github.com/cve-search/cve-search/archive/master.tar.gz | \
    tar xz -C ${CVE_BASE} --strip-components 1 --keep-newer-files
  pip3 install -r requirements.txt
}

function start_mongodb {
  if ! pidof -x "mongod" >/dev/null; then
    log "Starting mongodb server"
    if [ -d /persist ]; then
      log "Recovering persisted data"
      shopt -s dotglob
      mv /persist/db/* /data/db/
      mv /persist/configdb/* /data/configdb/
      rm -R /persist
    fi
    mongo-entrypoint.sh mongod --logpath /var/log/mongodb/mongod.log &
    sleep 5
  fi
}

function stop_mongodb {
  if pidof -x "mongod" >/dev/null; then
    log "Restarting mongodb server"
    kill $(pidof -x "mongod")
    sleep 5
  fi
}

function start_redis {
  if ! pidof -x "redis-server" >/dev/null; then
    log "Starting redis server"
    /etc/init.d/redis-server start
    sleep 2
  fi
}

function stop_redis {
  if pidof -x "redis-server" >/dev/null; then
    log "Restarting redis server"
    /etc/init.d/redis-server stop
    sleep 5
  fi
}

function populate_database {
  log "Populating database"
  ./sbin/db_mgmt.py -p
  log "db_mgmt_cpe_dictionary"
  ./sbin/db_mgmt_cpe_dictionary.py
  log "db_updater -c"
  ./sbin/db_updater.py -c
  log "db_mgmt_ref"
  ./sbin/db_mgmt_ref.py
}

function update_database {
  log "Updating database"
  ./sbin/db_updater.py -v
}

function repopulate_database {
  log "REPOPULATING database"
  ./sbin/db_updater.py -v -f
}

# Validate number of arguments
if [ $# -eq 0 ]
  then
    show_help
    exit 0
fi

# Parse arguments
while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
      -h|--help)
      show_help
      ;;
      -i|--initialize)
      update_repo
      start_mongodb
      start_redis
      populate_database
      stop_mongodb
      stop_redis
      ;;
      -u|--update)
      update_repo
      start_mongodb
      start_redis
      update_database
      ;;
      -r|--repopulate)
      update_repo
      start_mongodb
      start_redis
      repopulate_database
      ;;
      -w|--web)
      start_mongodb
      start_redis
      log "Starting web app"
      python3 ./web/index.py
      ;;
      *)
      show_help
      ;;
  esac
  shift
done

