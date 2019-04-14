#!/usr/bin/env bash

ansible-playbook --ask-vault-pass -i $1, provision.yml
