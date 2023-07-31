Applies the magic formula to Canadian (TSX) and US Stock Exchanges (NYSE)

Installation
-------------

Eventually you can just install this via PyPi and pip, but for now, just download
the git repo, and install the package into a virtual environment:

```
# create virtualenv
# you might need to: pip3 install virtualenv  (if you don't already have virtualenv installed)
virtualenv -p python3.10 --prompt="mf" .venv

# activate the new environment
source .venv/bin/activate

# update pip
pip install --upgrade pip

# if you're only interested in running mformula, you can install the runtime
# dependencies
pip install -r requirements.txt

# if you want to run the tests and contribute to the development, install the
# developer dependencies
pip install -r dev-requirements.txt
```

Usage
--------------

Once installed, you can run `mformula` on the command line to see usage.
