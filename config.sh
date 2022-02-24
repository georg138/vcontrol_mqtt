#!/bin/bash
./create_config.py
cp vito.xml /etc/vcontrold/
systemctl restart vcontrol
