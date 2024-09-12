#!/bin/bash

repo=$1
commit_id=$2
cd $repo
git show $commit_id --stat | grep -e 'insertions' -e 'deletions'

