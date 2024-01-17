# Django app for integration with Quickbooks Desktop
This is the django app for integration with QBD for lexul.

## Install Required Packages
   pip install -r requirements.txt

For queue, You need to install Redis on your machine.

If the OS is Windows,
## Install WSL2 on Windows 10

   Install WSL2

      install everything you need to run Windows Subsystem for Linux (WSL) by entering this command in an administrator PowerShell or Windows Command Prompt and then restarting your machine.
      
      command on Powershell: wsl --install

## Install Redis on server or machine

   Install Redis

      Once you're running Ubuntu on Windows, you can follow the steps detailed at Install on Ubuntu/Debian to install recent stable versions of Redis from the official packages.redis.io APT repository. Add the repository to the apt index, update it, and then install:

      curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

      echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

      sudo apt-get update
      sudo apt-get install redis

      Lastly, start the Redis server like so:

      sudo service redis-server start

   Connect to Redis
      You can test that your Redis server is running by connecting with the Redis CLI:

      ->redis-cli 
         127.0.0.1:6379> ping
         PONG



## Install PostgresSQL
## Running the Application
   After activate the venv

   python manage.py makemigrations

   python manage.py migrate
   
   python manage.py runserver
