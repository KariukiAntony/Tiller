#! /bin/bash

if [ "$DATABASE" == "postgres" ]; then
    echo "postgres starting in a few ..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
        echo "waiting for a tcp connection ..."
        sleep 0.1
    done

    echo "postgresql started"

fi
echo "running your flask application..."
exec "$@"
