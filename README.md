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

## Commands to checkout the code and push local changes.
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
2. Install [Angular-cli](https://cli.angular.io/)
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
1. Make sure you have python2, virtualenv installed on your machine
2. go to the backend folder, run the following commands to build the backend server

    `source venv/bin/activate`

    `export FLASK_APP=main.py`

    `flask run`

### Browser
After finishing set up the frontend and backend, open the browser(recommend chrome) and visit "http://localhost:4200/", you should be able to see the website connected with the backend

## TBD: Commands to send out code review

