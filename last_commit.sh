#!/bin/bash
echo "last_updated: \"$(git log -1 --format="%cd" --date=iso)\"" > _data/last_commit.yml