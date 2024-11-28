#!/bin/bash
export TZ="Europe/Paris"
echo "last_updated: \"$(git log -1 --format='%cd' --date=format-local:%d\ %B\ %Y\ %H:%M\ \(CET\))\"" > ./last_commit.yml