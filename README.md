# Wear OS DMM data sampling and graphing project for 2020 summer Intern

This is not an officially supported Google product.

This repository is based on a template that can be used to seed a repository for a
new Google open source project. See https://opensource.google/docs/releasing/

This template uses the Apache license, as is Google's default.  See the
documentation for instructions on using alternate license.
## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

    Copyright 2020 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

## Commands to checkout the code and push local changes (For admin only).
    git init

    git remote add origin git@github.com:googleinterns/power-data-graphing-intern-2020.git

    git checkout master

    git pull

    ...

    make local changes

    ...

    git add your_file_name

    git commit -m "Changes description"

    git push -u origin master

## Adding a new SSH key to your GitHub account for first-time user.

If you encountered "Permission denied (publickey), please set up SSH key following the instruction at:
https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account

## Build rules
### Frontend:
1. Install Angular denpendencies
    * Install [Node.js](https://nodejs.org/en/download/) & [npm](https://www.npmjs.com/get-npm)
    * Check Node.js version and npm version by entering

      `node -v`

      `npm -v`
2. Install [Angular-cli](https://cli.angular.io/) by running `npm install -g @angular/cli`
    * Check version by running
    
      `ng version`
    * Below are the hello world project's Angular version
        * @angular-devkit/architect    0.901.6
        * @angular-devkit/core         9.1.6
        * @angular-devkit/schematics   9.1.6
        * @schematics/angular          9.1.6
        * @schematics/update           0.901.6
        * rxjs                         6.5.4

3. go to fronend folder, and run following commands to build the frontend

    `npm install`

    `ng serve`

### Backend

#### Install pkgs

Make sure you have python3.7+, pip3, python3-venv installed on your machine

1. To check pip3 version, run `pip3 -V`, or run `sudo apt-get install python3-pip` to install it on your machine

2. Run `sudo apt-get install python3-venv` to install python3-venv.

#### Build and run the backend
1. Make sure you have a python virtual environment on your local machine and install all dependencies in the virtual environment.
    * Create a virtual environment by running `python3 -m venv venv`. (Recommend to put the environment folder at project's root folder)
    * Activate the environment by running `source venv/bin/activate`
    * `pip3 install wheel`
    * install packages in the environment by running `pip3 install 'package-name'`
2. go to the backend folder, run the following commands to build the backend server **Make sure that you are in a virtual environment before you run this command**
    * `pip3 install -r requirements.txt` (Only need to run this command at the first time)
    * `./build.sh`
3. Leave the virtual environment
    * `deactivate`

### Browser
After finishing set up the frontend and backend, open the browser(recommend chrome) and visit "http://localhost:4200/", you should be able to see the website connected with the backend.


## Dev Workflow

### One time actions:
1. Fork the repo
    * Done in github ui.
    * For example, my fork repo is https://github.com/yaomeng-google/power-data-graphing-intern-2020
2. Clone the forked repo locally
    * git clone git@github.com:<YOUR_USERNAME>/power-data-graphing-intern-2020.git
3. Add upstream remote
    * git remote add upstream git@github.com:googleinterns/power-data-graphing-intern-2020.git
    * Run “git remote -v”, the origin is the fork repo, upstream is the actual repo.
         * origin	git@github.com:yaomeng-google/power-data-graphing-intern-2020.git (fetch)
         * origin	git@github.com:yaomeng-google/power-data-graphing-intern-2020.git (push)
         * upstream	git@github.com:googleinterns/power-data-graphing-intern-2020.git (fetch)
         * upstream	git@github.com:googleinterns/power-data-graphing-intern-2020.git (push)

### When I am going to work on a new feature:
1. sync my fork's master branch to upstream's master branch
    * git checkout master; git fetch upstream; git rebase upstream/master
2. create a new branch from master
    * git checkout -b cool_feature
3. do my coding
4. add and commit my changes
    * git add *; git commit -m "New feature"
5. push my branch to my fork
    * git push origin cool_feature
6. pull-request my branch from my fork to the upstream repo
    * done in the git hub UI
7. deal with any code review code changes by making commits and updating the branch in my fork (this updates the open pull-request)
    * git add *; git commit -m "Fixes form review"; git push origin cool_feature
8. merge the branch into the upstream repo's main branch
    * done in github ui
9. delete my development branch
    * normally done in github ui


## TBD: Deploy the project to Google Cloud Platform
1. Download gcloud SDK by following this [link](https://cloud.google.com/sdk/install)
2. Initialze gcloud project by running `gcloud init`, auenticate with your google acount, and select the option of setting up a new project by entering a new project id, for tank-big-data-plotting, the project id is: google.com:tank-big-data-plotting-285623
3. Go to the /frontend folder, build the prod version of the frontend by entering `ng build --prod`. Then go to the generated /dist folder, run `gcloud app deploy`. Make sure if your gcloud project setup is correctly, and the target service is set as default
4. Go to the /backend folder, run `gcloud app deploy`, and make sure the target service is set as api.
5. Go to the gcp console and make sure the latest frontend and backend have been uploaded.
