<!-- Copyright 2023 Qarik Group, LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

<!-- LLM part is based on: https://gpt-index.readthedocs.io/en/stable/guides/tutorials.html -->

# Resume Chatbot

This project allows users to interact with resumes stored in PDF files and ask questions about a single person or a
group of people in plain English. Example questions:

- What are the top skills for [person name]?
- Tell me about [person name] strengths and weaknesses?
- Does [person name] have Java or Python experience?
- Where did [person name] work the longest?
- When did [person name] start working for Qarik?
- Compare and contrast the skills of [person name1] and [person name2].
- List all people with Kubernetes or GCP certifications.

Qarik employees can use an IAP secured application loaded with resumes of Qarik employees here:
[go/skills-bot](https://go/skills-bot). Here is an example of the UI running in a browser:

![Web UI screenshot with sample Q&A](./doc/images/chat-ui-screenshot.png)

If you found a bug, or have any ideas on how to improve this tool, please
[open an issue](https://github.com/Qarik-Group/resume-chatbot/issues), or better yet - submit a pull request.

## How does this app work?

The application is hosted on GCP as Cloud Run services. Resumes of multiple people uploaded in PDF format to the server
(currently just keeping a local copy inside of the docker image, but really needs to be on Drive or GCS). The backend is
built using Python and FastAPI. The bot uses OpenAI's LLM (Language Model) to generate answers to your queries. The bot
also uses LlamaIndex framework with LangChain to extract data from resumes uploaded into the system.

This application can be run on Linux or MacOS locally, or deployed on GCP in two modes (controlled by the "ENABLE_IAP"
flag in the root '.env' file):

1. Unprotected without using IAP, allowing users to connect directly to Cloud Run services.

2. Protected by IAP with IAM authentication prior to allowing users access to the frontend and backend Cloud Run
   services.

![Resume chatbot architecture](./doc/images/architecture.png)

_Note: Currently PDF files with resumes are statically stored locally in the [data](./components/server/data) directory
of the backend container, but in the future will be loaded and dynamically updated via GCS._

## Prerequisites

In order to build and deploy this project you need the following:

- ChatGPT API key
- Install GCLoud SDK
- Install Python 3.10+
- Install npm
- Google Cloud project (not needed if you simply want to run a local client and server)
- Ability to create external IP addresses in your GCP project (only if you decide to use IAP in front of Cloud Run)

## Setup

- [Create](https://console.cloud.google.com/projectcreate) a Google Cloud Platform (GCP) project.

- Clone the repo

  ```bash
  PROJECT_HOME=~/resume-chatbot
  git clone git@github.com:Qarik-Group/resume-chatbot.git "${PROJECT_HOME}"
  ```

- Copy template environment files:

  ```bash
  cp "${PROJECT_HOME}/.env.example" "${PROJECT_HOME}/.env"
  cp "${PROJECT_HOME}/components/server/.env.example" "${PROJECT_HOME}/components/server/.env"
  cp "${PROJECT_HOME}/components/client/.env.example" "${PROJECT_HOME}/components/client/.env"
  ```

- Update all three '.env' files created above with your own values, including the
  [OpenAI API Key](https://platform.openai.com/account/api-keys). Also check the ENABLE_IAP setting and set it to "true"
  if you want to enable IAP in front of your Cloud Run instances. However be aware that the initial setup will take more
  than an hour because it takes that long to propagate the SSL certificate settings.

- Add any number of PDF files with resumes to the [components/server/data](components/server/data/) folder. Files shall
  be named using 'Firstname Lastname.pdf' format with space separating first and last name. Optionally you can append
  'Resume' after last name. For example: 'Roman Kharkovski Resume.pdf'.

- Complete the setup:

  ```bash
  cd "${PROJECT_HOME}"
  ./setup.sh
  ```

## Test query engine

The experimentation with the queries can be done on a local machine:

- Activate the Python virtual environment in your terminal (only do it once in a terminal session):

  ```bash
  cd "${PROJECT_HOME}"
  source .venv/bin/activate
  ```

- Run the set of pre-built tests against the query engine, or use it in the interactive mode:

  ```bash
  cd components/server/dev
  ./test.sh
  ```

![Command line test for queries - screenshot](./doc/images/cmd-line-test-screenshot.png)

## Development

The development can be done on a local machine (everything, except for the ChatGPT itself), which can be your physical
machine, or a cloud based environment. You can run local Firestore emulator, the query engine server as the local Python
process (or as a local container), and run UI in a local NodeJS process (or a local container):

- In your terminal start the Firestore emulator:

  ```bash
  cd "${PROJECT_HOME}/components/server/dev"
  ./firebase_emulator.sh
  ```

- In another terminal window run the local instance of the server:

  ```bash
  cd "${PROJECT_HOME}"
  source .venv/bin/activate
  cd components/server/dev
  ./run_local.sh
  ```

- In another terminal run the local instance of the client:

  ```bash
  cd "${PROJECT_HOME}/components/client/dev"
  ./run_local.sh
  ```

- Once you open the local client UI in your browser, navigate to the "Settings" menu option and update the "Backend URL"
  to point to your local server: [http://127.0.0.1:8000](http://127.0.0.1:8000). If you want your client UI to always
  point to the local query engine instance, edit the [App.js](./components/client/src/App.js) and change the
  `defaultBackendUrl`.

## Deployment to GCP with security disabled (no IAP, no IAM)

This assumes that the initial setup was done using the `ENABLE_IAP=false` in the .env file at the root directory.

This assumes that the initial setup was done using the `ENABLE_IAP=false` in the .env file at the root directory.

- Build and deploy the query engine backend to Cloud Run:

  ```bash
  cd components/server/dev
  ./deploy.sh
  ```

- Update the [app.js](components/client/src/App.js) with the URL of your backend service deployed in the step above:

  ```javascript
  const serverBackendUrl = "https://<put-your-Cloud-Run-URL-here>.a.run.app";
  ```

- Build and deploy the UI service to Cloud Run:

  ```bash
  cd components/client/dev
  ./deploy.sh
  ```

- Open the chatbot web page using url from the deployment step above and interact with the bot.

## Deployment to GCP with security enabled (IAP and IAM)

- Change the `ENABLE_IAP=true` in the .env file at the root directory.

- Re-run the setup:

  ```bash
  cd "${PROJECT_HOME}"
  ./setup.sh
  ```

- Change the `ENABLE_IAP=true` in the .env file at the root directory.

- Re-run the setup:

  ```bash
  cd "${PROJECT_HOME}"
  ./setup.sh
  ```

- Build and deploy the server to Cloud Run:

  ```bash
  cd components/server/dev
  ./deploy.sh
  ```

- Get the external IP address 'skillsbot-backend-ip' for Backend service:

  ```bash
  gcloud compute addresses list
  ```

- Update the [app.js](components/client/src/App.js) with the proper backend IP (skillsbot-backend-ip), for example:

  ```javascript
  const serverBackendUrl = "https://11.22.33.444.nip.io";
  ```

- Build and deploy the UI to Cloud Run:

  ```bash
  cd components/client/dev
  ./deploy.sh
  ```

- Steps above create Self Signed Certificate and may take up to 1 hour to complete. Feel free to re-run the scripts.

- Open [IAP GCP Console](https://cloud.google.com/iap/docs/customizing#allowing_http_options_cors_preflight) and enable
  "HTTP Preflight" for CORS.

- Get the external IP address 'skillsbot-ui-ip' for UI service:

  ```bash
  gcloud compute addresses list
  ```

- In GCP Console create the OAuth Consent Screen (here is a
  [good article](https://blog.logrocket.com/guide-adding-google-login-react-app/) that describes some of these
  concepts):

- Make it internal application

- Use Authorized domain: URI of your UI Cloud Run Service without the 'https://' part, and if you are using the IAP,
  also add use '<UI_IP_ADDRESS>.nip.io'

- Add scopes: './auth/userinfo.email' and './auth/userinfo.profile'

  These changes may take from few minutes to hours to propagate, but the good news you only need to do it once.

- Open the chatbot web page using url [https://<UI_IP_ADDRESS>.nip.io] and interact with the bot.
