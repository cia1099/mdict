#!/bin/bash
set -e;
cd ~/project/dict
rm dict_oxfordstu.log
source venv/bin/activate
python3 oxfordstu/create_oxfordstu_db.py
