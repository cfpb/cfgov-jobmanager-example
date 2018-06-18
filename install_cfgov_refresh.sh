#!/bin/sh

git clone https://github.com/cfpb/cfgov-refresh
cd cfgov-refresh
pip install -r requirements/wagtail.txt
pip install -r requirements/libraries.txt
pip install -r requirements/test.txt

# Necessary for jobmanager, since it will exist in two places
rm -rf cfgov/jobmanager 
