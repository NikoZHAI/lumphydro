# lumphydro
WEB APP of Model HBV96 (BETA)

This application is not deployed yet. In order to use please make sure that you have already installed Python 2 (>=2.7.9). Once you have Python installed, open a console(Terminal, not a python console) and install all the dependencies in the file **`dependency`**, preferably using **`pip`**:


```
cd ../YourPath/lumphydro
pip install -r dependency
```

Now the App is ready to run. You can simply change directory to the **`lumphydro`** root (where exists the **`manage.py`** file). Tap in your console:


`python manage.py runserver`


Then open the link (**http://127.0.0.1:8000/hbv96/**) in the console with the latest **_Google Chrome_**. Multi-browser support will be done before realease.


You are ready to go ! I wish you good fortune, in the modellings to come !


Niko ZHAI


If you do not want to mess up your Python environment, it is recommanded to use `pyenv` to manage your Python version and packages.


To install `pyenv` : `pip install --egg pyenv`

**WARNING** still a very hacky proof of concept. Does not work with Python 3 at all yet and in Python 2 only with the use of the --egg parameter. Check the normal way to install `pyenv` on [GitHub](https://github.com/pyenv/pyenv).


To install `pyenv-virtualenv`, check out [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv).


To set up a virtual Python enviroment : `pyenv virtulaenv $YOUR_ENVIRONMENT_NAME (hbv96 for example)`


And activate it : `pyenv activate $YOUR_ENVIRONMENT_NAME`


Then you have your specific Python environment for HBV WEB.
