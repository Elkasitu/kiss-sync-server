#!/usr/bin/env python3

import psycopg2
import sys


from flask import Flask, request, jsonify
app = Flask(__name__)


__version__ = '0.1.1'
__author__ = "Elkasitu"


def bootstrap():
    try:
        # TODO: dbname and user as settings? for security
        conn = psycopg2.connect("dbname=kiss user=postgres")
    except psycopg2.OperationalError:
        # TODO: automatically create the database
        print("Database `kiss` does not exist, try creating it with the `createdb` command")
        sys.exit(1)
    create_tables(conn)
    # TODO: try to find a better way to do this
    return conn


def create_tables(conn):
    cr = conn.cursor()
    try:
        return cr.execute("SELECT 1 FROM videos")
    except psycopg2.errors.UndefinedTable:
        conn.rollback()
    # TODO: move this to a base.sql that gets imported automatically
    cr.execute("CREATE TABLE videos (id serial PRIMARY KEY, name varchar, time float DEFAULT 0.0);")
    conn.commit()


@app.route('/add', methods=['POST'])
def add():
    content = request.get_json()
    # TODO: use a sha-1/md5 hash of the file
    name = content['name']
    cr = conn.cursor()
    cr.execute("INSERT INTO videos (name) VALUES (%s)", (name,))
    conn.commit()
    return jsonify({'res': 'ok'})


@app.route('/remove', methods=['POST'])
def remove():
    content = request.get_json()
    name = content['name']
    cr = conn.cursor()
    cr.execute("DELETE FROM videos WHERE name=%s", (name,))
    conn.commit()
    return jsonify({'res': 'ok'})


@app.route('/update', methods=['POST'])
def update():
    content = request.get_json()
    name = content['name']
    time = content['time']
    cr = conn.cursor()
    cr.execute("UPDATE videos SET time=%s WHERE name=%s", (time, name,))
    conn.commit()
    return jsonify({'res': 'ok'})


@app.route('/fetch/<string:name>')
def fetch(name):
    cr = conn.cursor()
    cr.execute("SELECT time FROM videos WHERE name=%s", (name,))
    time = cr.fetchone()
    return jsonify({'time': time and time[0]})


if __name__ == '__main__':
    conn = bootstrap()
    app.run(host='0.0.0.0')
