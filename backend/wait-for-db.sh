#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
shift
cmd="$@"

until nc -z db 3306; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "MySQL is up - executing command"
exec $cmd
