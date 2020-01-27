import argparse
import os
import datetime
import sys
from jira import JIRA
from configobj import ConfigObj
from github import Github

def main(argv):
     
    today = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    
    # Configuration file (required, assume it's in the same dir as script, option to specify a new config available)
    config_file = 'jira2html.conf'
    
    # Set up argument parser (none required)
    parser = argparse.ArgumentParser(description='Process input arguments.')
    parser.add_argument('-u', metavar='<user>', dest='usr', help='JIRA user name. Required if not set via the env. variable JIRA_USR.')
    parser.add_argument('-p', metavar='<password>', dest = 'pwd', help='JIRA user password. Required if not set via the env. variable JIRA_PWD.')
    parser.add_argument('-c', metavar='<config_file>', dest='config_file', help='Absolute path to config file. If not present, will look for ./jira2html.conf')

    # Parse arguments
    args = parser.parse_args()
    
    if (args.config_file != None):
        config_file = args.config_file
    
    if (args.usr == None and args.pwd == None):
        try: 
            usr = os.environ['JIRA_USR']
            pwd = os.environ['JIRA_PWD']
        except:
            print("Error: server authentication information (user and/or password) is missing.\n")
            parser.print_help()
            sys.exit(1)
    else:
        usr = args.usr
        pwd = args.pwd
        
        
    # Read config file
    try:
        config = ConfigObj(config_file)
    except:
        print("Error: config file not found or unreadable.\n")
        
    jira_url = config['jira_url']   
    try:    
        jira = JIRA(jira_url, basic_auth=(usr, pwd))
    except:
        print("Error: JIRA server authentication failed.\n")
        sys.exit(1)
    
    issues = jira.search_issues('project="' + config['jira_project'] + '"',maxResults=0)
    issues.sort(key=lambda x: x.key, reverse=True)
    
    issues_table = create_issues_table(jira_url, issues, config['status_filter'])
    
    # Connect to git repo
    try:
        g = Github(config['git_token'])
    except:
        print("Error: git authentication failed.\n")
        sys.exit(1)
        
    repo = g.get_repo(config['git_repo'])
    
    # Push changes to git
    try:
        content = repo.get_contents(config['md_file'])
    except:
        print("Warning: target not found, a new file will be created.\n")

    if content == None:
        new_content = create_header(config['commit_message'], 'Auto-generated issues list from JIRA') + '\n' + issues_table
        repo.create_file(config['md_file'], config['commit_message'] + " " + str(today), new_content, branch="master")
    else:
        tmp = content.decoded_content.decode("utf-8").split("\n")
        # Remove current header
        current_text = ""
        for i in range(7, len(tmp)):
            current_text += tmp[i] + "\n"
        # Remove existing table
        edited_current = current_text[:current_text.rfind('<table')]
        new_content = create_header(config['commit_message'], "Auto generated issues list from JIRA") + "\n" + edited_current + issues_table
        repo.update_file(content.path, config['commit_message'] + " " + str(today), new_content, content.sha, branch="master")
        
    print("Update pushed, all done!")
        
                
def create_issues_table(jira_url, issues, status_filter):
    
    status = {'Open':'#E0E0E0', 'In Progress':'#B3F0FF', 'Selected':'#E0E0E0', 'To Do':'#E0E0E0', 'Done':'#009A00', 'Resolved':'#009A00'}
    if (status_filter == 'True'):
        status = {'Open':'#E0E0E0', 'In Progress':'#B3F0FF', 'Selected':'#E0E0E0', 'To Do':'#E0E0E0'} 
        
    text = \
        '<table border="0" cellpadding="0" cellspacing="1">\n' + \
        '<theader>\n' + \
        '    <tr align="center" style="background-color: #60a9a9;" valign="middle">\n' + \
        '        <td>ISSUE</td>\n' + \
        '        <td>SUMMARY</td>\n' + \
        '        <td>PRIORITY</td>\n' + \
        '        <td>STATUS</td>\n' + \
        '    </tr>\n' + \
        '</theader>\n' + \
        '<tbody>\n'
        
    for issue in issues:
        if (len(status) != 0 and issue.fields.status.name not in status.keys()):
                continue
        text += \
        '    <tr>\n' + \
        '        <td><a href="' + jira_url  + '/browse/' +  issue.key + '">' + issue.key + '</a></td>\n' + \
        '        <td>' + issue.fields.summary + '</td>\n' + \
        '        <td>' + issue.fields.priority.name + '</td>\n' + \
        '        <td style="background-color:' + status[issue.fields.status.name] + '">' + issue.fields.status.name + '</td>\n' + \
        '    </tr>\n'
        
    text +=    '</tbody>\n' + \
        '</table>\n'
    return text

                
def create_header(title, description, published='true'):
    return '---\n' + \
             'title: ' + title + '\n'+ \
             'description: ' + description + '\n'+ \
             'published: ' + published + '\n'+ \
             'date: ' + str(datetime.datetime.today()) + '\n'+ \
             'tags: \n' + \
             '---'
             
if __name__ == '__main__':
    main(sys.argv[1:])
