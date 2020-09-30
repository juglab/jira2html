# jira2html
Automatically output a list of JIRA issues to an HTML table and push them to a git-hub repository. The original target for this exercise was a page to be published to a Wiki.js wiki backed by git.

## Required packages:

* [PyGithub](https://github.com/PyGithub/PyGithub): pip install PyGithub
* [JIRA Python](https://jira.readthedocs.io/en/latest/installation.html): pip install jira
* [ConfigObj](https://configobj.readthedocs.io/en/latest/configobj.html): pip install configobj

## How to:

* You need have to create a GitHub access token [here](https://github.com/settings/tokens) (Select only 'repo' as scope).
* You need to provide your JIRA authentication parameters either as the environment variables (JIRA\_USR and JIRA\_PWD] or as arguments to the script. Note: for a hosted server the "password" will be the user's password, but for a cloud instance this has to be a token, instructions on how to get one are [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html)
* You need to create a configuration files using the provided template. The script will automatically look for a local configuration file named "jira2html.conf", 
  but you can also use the "-c" command line option to specify an alternative configuration file

The configuration file must contain:

```
# Template config file for jira2md.py
jira_url=                           # URL of your JIRA server
jira_project=                       # Your JIRA project code
jira_usr=                           # Your JIRA username
jira_token=                         # Your JIRA API access token
git_token=                          # Obtained from https://github.com/settings/tokens
git_repo=                           # yourOrg/yourRepo
commit_message=                     # Git commit message
status_filter=True                  # If true shows only open and in progress issues, set to false for all issues
md_file=                            # git repo path of output file
```

A configuration file template is included in the repository. To use rename to jira2html.conf and fill in.

## Usage

```
>> python jira2html.py [-u <user>] [-p <password>] [-c <configFile>]
```
