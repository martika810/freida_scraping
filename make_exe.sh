#!/usr/bin/sh

echo '################################'
echo '#   Creating wheel files ...####'
echo '################################'

pip3 wheel -w . .

echo '################################'
echo '#   Creating pex files   ...####'
echo '################################'

pex --python=python3 --disable-cache -f $PWD freida_scraping  -e src.webapp -o freida_scraping

echo '################################'
echo '#   Deleting wheel files ...####'
echo '################################'

rm *.whl
rm progress.pickle
