#!/usr/bin/python3

# FUCK PYTHON


# Copyright (C) 2015 Martin Sandsmark <martin.sandsmark@kde.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from subprocess import call
import fcntl
import json
import os
import pprint
import re
import sys
import traceback
import urllib.request

USERNAME = 'sandsmark'

# directory where you want your preciouses stored
os.chdir('/srv/http/iskrembilen/git')

def download_repo(name, url, description):
    call(['git', 'clone', '--mirror', url])
    origdir = os.getcwd()
    os.chdir(origdir + '/' + name)
    call(['git', 'config', '--local', '--add', 'gitweb.description', description])
    os.chdir(origdir)

def update_repo(name, url, description):
    origdir = os.getcwd()
    os.chdir(origdir + '/' + name)

    if call(['git', 'fetch', '--force']) is not 0:
        os.chdir(origdir)
        print('unable to fetch', url)
        return

    call(['git', 'config', '--local', '--unset-all', 'gitweb.description'])
    call(['git', 'config', '--local', '--add', 'gitweb.description', description])

    os.chdir(origdir)

def fetch_url(url, description):
    repo_res = re.search(r'git://github\.com/' + USERNAME + r'/([^\.]+\.git)', url)
    if not repo_res:
        print('unable to parse url:', url)
        return False

    repo_name = repo_res.group(1)
    if os.path.isdir(os.getcwd() + '/' + repo_name):
        update_repo(repo_name, url, description)
    else:
        download_repo(repo_name, url, description)


# Running multiple instances would be really bad
fp = open('/run/lock/github-mirror.lock', 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print('Unable to lock lockfile, already running?')
    sys.exit(1)

url = 'https://api.github.com/users/' + USERNAME + '/repos?per_page=100'

while url:
    response = urllib.request.urlopen(url)
    repos_res = response.readall().decode('utf-8')
    repos = json.loads(repos_res)

    if not repos:
        print('could not download repos')
        print(repos_res)

    for repo in repos:
        if 'git_url' not in repo:
            print('could not find git_url in repo')
            pprint.pprint(repo)
            break

        if not 'description' in repo:
            repo['description'] = ''

        try:
            fetch_url(repo['git_url'], repo['description'])
        except:
            print('failure to fetch repo ' + repo['git_url'])
            traceback.print_exc()

    # fucking github limits the number of repos on a page...
    link_header = response.getheader('Link')
    if not link_header:
        break
    find_url_res = re.search(r'^<([^>]+)>; rel="next"', link_header)
    if find_url_res is None:
        break

    url = find_url_res.group(1)


