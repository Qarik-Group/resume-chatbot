<!--
Copyright 2023 Google LLC
Copyright 2023 Qarik Group, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

# Resume Chatbot

This project demonstrates the use of the following LLMs for the purpose of Q&A over PDF files with resumes:

- Open AI ChatGPT (using LlamaIndex)
- Google PaLM2 (using LangChain)
- Google Gen AI Enterprise Search with summarization (using direct API)
- Google Vertex AI (using LangChain, Google embeddings and bison model, Chroma as vector DB)

This project allows users to interact with resumes stored in PDF files and ask questions about a single person or a
group of people in plain English. Example questions:

- What are the top skills for [person name]?
- Tell me about [person name] strengths and weaknesses?
- Does [person name] have Java or Python experience?
- Where did [person name] work the longest?
- When did [person name] start working for Qarik?
- Compare and contrast the skills of [person name1] and [person name2].
- List all people with Kubernetes or GCP certifications.

Qarik employees can use an IAP secured application loaded with resumes of Qarik staff:
[go/skills-bot](https://go/skills-bot).

Here is an example of the UI running in a browser:

![Web UI demo](./doc/images/demo.gif)

If you found a bug, or have any ideas on how to improve this tool, please
[open an issue](https://github.com/Qarik-Group/resume-chatbot/issues), or better yet - submit a pull request.

## How does this app work?

The application is hosted on GCP as Cloud Run services. Resumes of multiple people uploaded in PDF format to the GCS
bucket and can be updated, deleted or changed at any time. The backend is built using Python and FastAPI. The bot uses
several different LLM implementations to generate answers to your queries. The bot also uses LlamaIndex framework with
LangChain to extract data from resumes uploaded into the system.

This application can be run on Linux or MacOS locally, or deployed on GCP in two modes (controlled by the "ENABLE_IAP"
flag in the root '.env' file):

1. Unprotected without using IAP, allowing users to connect directly to Cloud Run services.

2. Protected by IAP with IAM authentication prior to allowing users access to the frontend and backend Cloud Run
   services.

![Resume chatbot architecture](./doc/images/architecture.png)

_Note: When developing or debugging on a local machine (UI and backend can run as a process or in a container), then PDF
files with resumes are statically stored locally in file system. When running on GCP, the resume files are re-downloaded
from the GCS bucket every time there is a change in one or more objects in the bucket._

## Prerequisites

In order to build and deploy this project you need the following:

- ChatGPT API key
- Google PaLM key (use https://makersuite.google.com)
- Allow listed account for Google Gen AI Enterprise Search
- Meta Llama 2 key
- Install GCLoud SDK
- Install Python 3.10+
- Install npm
- Google Cloud project (not needed if you simply want to run a local client and server)
- Ability to create external IP addresses in your GCP project (only if you decide to use IAP in front of Cloud Run)

## Setup

- [Create](https://console.cloud.google.com/projectcreate) a Google Cloud Platform (GCP) project with assigned billing
  account.

- Enable Gen App Builder in your project as described in the
  [documentation](https://cloud.google.com/generative-ai-app-builder/docs/before-you-begin).

- Clone the repo

  ```bash
  PROJECT_HOME="${HOME}/resume-chatbot"
  git clone git@github.com:Qarik-Group/resume-chatbot.git "${PROJECT_HOME}"
  ```

- Copy template environment file:

  ```bash
  cd "${PROJECT_HOME}"
  cp .env.example .env
  ```

- Update the '.env' file with your own values, including the
  [OpenAI API Key](https://platform.openai.com/account/api-keys) and any other relevant information for your
  organization or project.

  - Check the `ENABLE_IAP` setting and set it to `true` if you want to enable IAP in front of your Cloud Run instances.
    However aware that the initial setup will take more than an hour because it takes that long to propagate the SSL
    certificate settings. I recommend setting `ENABLE_EAP` to `false` for the simple development and experimentation.

- Add any number of PDF files with resumes to the [data](data) folder. The implementation detail of LlamaIndex and
  ChatGP in this project uses specific naming for resume files. Specifically, files shall be named using 'Firstname
  Lastname.pdf' format with space separating first and last name. Optionally you can append 'Resume' after last name.
  For example: 'Roman Kharkovski Resume.pdf'. The Google PaLM and Enterprise Search implementations do not require any
  specific naming of files, therefore if you want to load up financial documents, technical documentation, user manuals,
  etc. it will still work ok.

- Optional (only if you need plan to run services locally for test or dev): Install Node.js and React:

```bash
brew update
brew install node
cd "${PROJECT_HOME}/components/client"
npm i react-scripts
```

- Create new virtual environment (if VSCode prompts you to switch to this new virtual environment, accept it). You may
  decide to have a separate Virtual Environment for each service, or have one common for all services:

  ```bash
  cd "${PROJECT_HOME}"
  python3 -m venv .venv
  ```

- Activate the Python virtual environment in your terminal (only do it once in a terminal session):

  ```bash
  source "${PROJECT_HOME}/.venv/bin/activate"
  ```

- Optional (only if you need plan to run services locally for test or dev): Install proper Python modules:

  ```bash
  cd "${PROJECT_HOME}/components"
  pip install -r ./common/requirements.txt -r ./query_engine/requirements.txt -r ./resume_manager/requirements.txt"
  ```

- Complete the setup:

  ```bash
  cd "${PROJECT_HOME}"
  ./setup.sh
  ```

## Deployment to GCP without IAP

This assumes that the initial setup was done using the `ENABLE_IAP=false` in the .env file at the root directory.

- Build and deploy all components:

  ```bash
  cd $PROJECT_HOME
  ./deploy.sh
  ```

Done! Now lets test the application:

- Open GCP Console, navigate to Cloud Run Page in your project.

- Open the details of the service `skillsbot-backend`. Copy the URL of the service into the clipboard (see image below).

![Service details in Cloud Console](./doc/images/backend_service_details.png)

- Open the details of the service `skillsbot-ui`. Open the service URL in a new browser tab to load the UI.

- In the Resume Chatbot UI, click on the `Config` item in the menu. In the field `Backend REST API URL` insert the URL
  of the `skillsbot-backend` service you copied into the clipboard earlier.

- Check all resumes available for queries by opening `Resumes` menu, or start asking questions about people in the
  `Chat` menu of the UI.

Optional - if you do not want to manually put a backend URL every time you open UI, you can permanently add backend UI
URL to the page source code:

- Update the [app.js](components/client/src/App.js) with the URL of your backend service deployed in the step above:

  ```javascript
  const serverBackendUrl = "https://<put-your-QUERY-ENGINE-CloudRun-URL-here>.a.run.app";
  ```

- Re-build and deploy the updated UI service:

  ```bash
  cd components/client/dev
  ./deploy.sh
  ```

- Open the chatbot web page using url from the deployment step above and interact with the bot. At this point all
  services should work, except for the Google Enterprise Search. To enable Google Enterprise Search, refer to the
  section below.

- Optional: If you are using sensitive data (such as your company financial, or other documents) in this project, you
  either must enable IAP to protect your deployed Cloud Run instances, or, make those instances visible only to internal
  VPC traffic and access them using the [Cloud Run proxy](https://github.com/GoogleCloudPlatform/cloud-run-proxy).

## Create Google Enterprise Search Gen AI App

Follow
[instructions to create Google Gen AI App](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#create_and_preview_a_search_app_for_unstructured_data_from)
using the section of the tutorial titled "Create and preview a search app for unstructured data from Cloud Storage".

When creating a datasource, point it to the GCS bucket with original PDF resumes, for example
`resume-originals-${PROJECT_ID}`. The import of data may take significant time - possibly as long as an hour.

While data import is in progress, open the [goog_search_tools.py](./components/query_engine/goog_search_tools.py) file
and update the value of the variables according to your Google Enterprise Search App you just created, for example, as
shown below:

```python
LOCATION = 'global'
DATA_STORE_ID = 'resume-sources_1693859982932'
SERVING_CONFIG_ID = 'default_config'
```

You can find the Data Store ID in the GCP Console:

![Data Store ID](/doc/images/data_store_id.png)

Redeploy the query service:

```bash
cd ${PROJECT_HOME}/components/query_engine
./deploy.sh
```

Whenever the Enterprise Search data import is complete, the query service will start using it as one of the LLM
backends. You can monitor the progress of data import by opening the console and checking the Data status under your app
in Gen AI builder:

![Data source import status](doc/images/ent_search_data_import.png)

Make sure to enable `Advanced LLM features` in the advanced application configuration:

![Advanced LLM features](doc/images/llm_features_toggle.png)

## Deployment to GCP with IAP (advanced and more secure)

- Update the `.env` file in the project home and set `ENABLE_IAP=true`.

- Prepare IAP related artifacts, including certificates, etc. Because of the certificate, it may take about an hour to
  propagate the proper data across GCP for IAP to work. This is only a one time step. Subsequent deployments in IAP
  enabled configuration are no different than a direct Cloud Run deployment.

  ```bash
  cd $PROJECT_HOME
  ./setup.sh
  ```

- Rebuild and redeploy all components:

  ```bash
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

## Test query engine locally

The experimentation with the queries can be done on a local machine:

- Run the set of pre-built tests against the query engine, or use it in the interactive mode:

  ```bash
  cd components/query_engine/dev
  ./test.sh
  ```

![Command line test for queries - screenshot](./doc/images/cmd-line-test-screenshot.png)

## Development

The development can be done on a local machine (everything, except for the remote APIs), which can be your physical
machine, or a cloud based environment. You can run local Firestore emulator, the query engine server as the local Python
process (or as a local container), and run UI in a local NodeJS process (or a local container):

- In your terminal start the Firestore emulator:

  ```bash
  cd "${PROJECT_HOME}/components/query_engine/dev"
  ./firebase_emulator.sh
  ```

- In another terminal window run the local instance of the query engine:

  ```bash
  cd "${PROJECT_HOME}"
  source .venv/bin/activate
  cd components/query_engine/dev
  ./run_local.sh
  ```

- In another terminal run the local instance of the client:

  ```bash
  cd "${PROJECT_HOME}/components/client/dev"
  ./run_local.sh
  ```

- Once you open the local client UI in your browser, navigate to the "Settings" menu option and update the "Backend URL"
  to point to your local server: [http://127.0.0.1:8000](http://127.0.0.1:8000).

# Replacing resumes with your own data

If you have working project with resume data and need to try it out with different type of data (financial statements,
or something else):

- Delete resume files from the GCS bucket with source resumes (`resume-originals-${PROJECT_ID}`) and upload your own
  files into it.
- Delete VertexAI index (refer to the `components/setup/delete_index.sh` script).
- Run VertexAI setup (`components/setup/delete_index.sh`). resumes.

# Credits

Various parts of this project were derived from Open Source tutorials an blog articles:

- Google Vertex Ai [tutorials]() and
  [notebooks](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/use-cases/document-qa/question_answering_documents_langchain_matching_engine.ipynb)
- LlamaIndex
  [tutorials](https://github.com/jerryjliu/llama_index/blob/main/docs/end_to_end_tutorials/question_and_answer/unified_query.md).
- LangChain [tutorials]()
