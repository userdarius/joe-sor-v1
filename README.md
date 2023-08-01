# Joe Smart Order Router

The Joe Smart Order Router is an offchain linear optimization of the LBQuoter contract for routing orders across pools for best price execution. 

This is a wip. A lot of the code and classes will be moved around and reimplemented. Right now, most classes are used for fetching and storing Barn API data to a class and most of the router logic is in main.py. Swap simulation logic is also in main.py
## Setting up the project
### Installing poetry
Poetry documentation can be found [here](https://python-poetry.org/docs/)
#### Using pipx 
Open your terminal and type the following command:

```pipx install poetry```

#### With the official installer 
Open your terminal and type the following command:

- Linus, MacOS, Windows (WSL) :

```curl -sSL https://install.python-poetry.org | python3 -```

- Windows (PowerShell) :

```(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -```

### Cloning the repo
In your terminal type :

```git clone https://github.com/userdarius/joe-sor-v1.git```

### Installing dependencies
Open the project and run :

```poetry install```

### Running the program 
Once the dependencies are installed go into the src folder in your terminal and run :

```poetry run python main.py```

(Once the project will be updated you will simply need to run poetry run with the parameters you wish to input)