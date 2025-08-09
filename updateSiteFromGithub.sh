#!/bin/bash

# Load ssh agent & code
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/rsa_github_toerns

# update files from github repo
git pull git@github.com:volkerpetersen/andreas_django.git
