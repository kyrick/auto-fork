# Auto Fork

[Click here to try out the service](http://auto-fork.us-east-1.elasticbeanstalk.com) 


`Auto Fork` is a Python Flask app that forks it's own repository to the users account.
The app uses a GitHub OAuth app to service authentication. 
Once authentication is complete the user can click a button to fork the code base into their github account.

# Tests


# Run locally

Before running locally, you will need a GitHub OAuth app. [Learn more about setting one up here.](https://docs.github.com/en/developers/apps/creating-an-oauth-app)

1. Configure the GitHub OAuth 
    * Homepage URL: http://localhost:5000/
    * Authorization callback URL: http://localhost:5000/auth
1. In a terminal cd to the project directory
1. `touch .env`
1. `vi .env` and add the following lines 
    * export AF_CLIENT_ID=your_client_id
    * export AF_CLIENT_SECRET=your_client_secret
1. `docker build . -t autofork`
1. `docker run -d -p 5000:5000 --env-file .env autofork`

