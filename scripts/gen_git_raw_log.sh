#!/bin/bash

repo=$1
since=$2
until=$3

cd $repo
git log --all --since=$since --until=$until --author "intel.com" > raw_git.log
