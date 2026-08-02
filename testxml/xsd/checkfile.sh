#!/usr/bin/env bash

xmllint --format --schema tmw.xsd "${1}" 2>&1 >/dev/null | \
    grep -v ": Skipping import of schema located at " | \
    grep -v ".xml validates"
