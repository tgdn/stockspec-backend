# AlertMap

## Getting the code

Fire up a terminal session and go wherever you want you code to live, then clone the repo.

    git clone https://github.com/tgdn/alertmap-backend.git

    cd alertmap-backend

## Installation

The following will apply to all Unix based operating systems (Linux, macOS etc).

### Homebrew (mac only)

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

    brew install python3.8

The above will install brew and python3.8 on your mac.

**For non mac users, install python3.8 using your distribution's package manager.**

### Virtual environment and dependencies

    # install virtualenv
    python3.8 -m pip install virtualenv
    # create virtualenv
    virtualenv -p $(which python3.8) venv
    # enter virtualenv
    source venv/bin/activate
    pip install -r requirements.txt

Now you've created your virtual environment, and installed the dependencies necessary to work.

### Create a superuser

To interact with the app and have access to the site admin you need a superuser account, let's create one.

The following command will prompt you for a username, email and password.

    python manage.py createsuperuser

Once it is complete, you have a superuser account created on your local database with which you can login.

## Running server

To run the django development server, simply execute the following command

    python manage.py runserver

If everything goes according to plan, you should have no error message, and you should have the server running on port 8000.

Visit [http://localhost:8000/admin](http://localhost:8000/admin) and if it works try to log in with the superuser credentials you created earlier.

**To stop the server, simply hit `Ctrl-C`**.

**To exit the virtual environment run the following**

    deactivate


## General workflow

### Enter virtualenv

    source venv/bin/activate

### Git

    # To start working on a new feature or fix create a new branch
    git checkout -b feature/feature-name

    # To change branch
    git checkout [branchname]

    # to add files to the index
    git add [file1 file2 file3 ...]

    # to commit
    git commit -m 'Your commit message'

    # to push to a branch
    git push origin [branchname]

    # to pull latest changes
    git pull origin [branchname]

### Development

Whenever you start working or anytime you go back to your computer and work on this, please pull the latest changes from the repository.
This will avoid conflicts and unnecessary merge commits.

    git pull origin [your-current-branch-name]

**Code, code, code**

**Commit and push**

A rule of thumb: commit as often as possible.

    git add [files...]
    git commit -m 'Commit message'
    git push origin [your-current-branch-name]

Please write clear commit messages.
