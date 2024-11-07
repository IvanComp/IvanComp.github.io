#!/bin/bash
echo "last_updated: \"$(git log -1 --format='%cd' --date=format-local:%d\ %B\ %Y\ %H:%M\ \(UTC\))\"" > _data/last_commit.yml