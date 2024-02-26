## Virtual Environments

To create one
`python3 -m venv .venv`

To activate it and get a nice clean package context
`source .venv/bin/activate`

To install packages for _this_ project
`pip3 install -r requirements.txt`

To add packages to this project (You should be in the virtual environment or you're going to have a bloated `requirements.txt`)
`pip3 install <package>`
`pip3 freeze > requirements.txt`

To get back to your home package context
`deactivate`
