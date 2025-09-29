#!/bin/sh
cat $1 | cut -f2- -d',' | sort -k 1 | python ../wsprmap.py
