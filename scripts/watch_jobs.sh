#!/usr/bin/env bash

while true; do
  clear
  echo "Latest jobs:"
  sqlite3 -header -column data/db/horrorverse.sqlite3 \
    "SELECT id, status, attempts FROM jobs ORDER BY id DESC LIMIT 10;"
  sleep 1
done
