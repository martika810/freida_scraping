#!/usr/bin/sh

echo '################################'
echo '#   Creating wheel files ...####'
echo '################################'

python setup.py install

echo '################################'
echo '#   Creating executable...  ####'
echo '################################'

pyinstaller --add-data "src/templates;templates" --one-file src/webapp.py

echo '################################'
echo '#   Deleting wheel files ...####'
echo '################################'
exit(
rm progress.pickle
