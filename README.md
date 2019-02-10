

brew install rabbitmq  - to install rabitmq

brew services start rabbitmq

rabbitmq-server   - to run it locally


list the queues : sudo rabbitmqctl list_queues

ensure pip,setuptools and wheel are installed:
    python -m pip install --upgrade pip setuptools wheel

    note : run this before :
        pip3 wheel -w . .


    pex --python=python3 -r requirements.txt -f . webscraper -e webscraper.run -o webscraper.pex


python setup.py sdist
python setup.py bdist_wheel

python setup.py install

pex ./