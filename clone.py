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


import json
import urllib.request
import json
import re
from pprint import pprint
import os
from subprocess import call

USERNAME = 'sandsmark'

def download_repo(url):
#    print('downloading new repo ', url)
    call(['git', 'clone', url])

def update_repo(name, url):
#    print('updating repo', name, url)

    origdir = os.getcwd()
    os.chdir(origdir + '/' + name)

    if call(['git', 'fetch', '--all']) is not 0:
        os.chdir(origdir)
        print('unable to fetch', url)
        return

    if call(['git', 'reset', '--hard', 'origin/master']) is not 0:
        os.chdir(origdir)
        print('unable to reset', name)
        return

    if call(['git', 'pull']) is not 0:
        os.chdir(origdir)
        print('unable to pull')
        return

    os.chdir(origdir)

def fetch_url(url):
#    print('getting url', url)
    repo_res = re.search(r'git://github\.com/' + USERNAME + r'/([^\.]+)\.git', url)
    if not repo_res:
        print('unable to parse url:', url)
        return False

    repo_name = repo_res.group(1)
    if os.path.isdir(os.getcwd() + '/' + repo_name):
        update_repo(repo_name, url)
    else:
        download_repo(url)


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
            fetch_url(repo['git_url'])
            break

        fetch_url(repo['git_url'])

    # fucking github limits the number of repos on a page...
    link_header = response.getheader('Link')
    if not link_header:
        break
    find_url_res = re.search(r'^<([^>]+)>; rel="next"', link_header)
    if find_url_res is None:
        print("unable to find next url", link_header)
        break

    url = find_url_res.group(1)


