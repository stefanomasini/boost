# Development

### Pre-requisites

- Python 3.5
    - Use PyEnv to set up the specific python version: 
        - `pyenv local 3.5.7`
        - `pyenv shell`
- NodeJS
- Yarn

### Install dependencies

    pipenv install (or maybe pipenv install --skip-lock)
    cd frontend
    yarn

### Run tests

    pipenv run python run-tests.py
    
### Run backend server for development

    pipenv run python server-dev.py
    
### Run frontend server for development

    cd frontend
    yarn start
