/* Copyright 2023 Qarik Group, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */

import React, { useState, useEffect } from "react";
import Alert from "@mui/material/Alert";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  ListItem,
  ListItemText,
  List,
  Drawer,
  TextField,
  Button,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { styled } from "@mui/system";
import { CircularProgress } from "@mui/material";
import { useGoogleLogin } from "@react-oauth/google";
import GoogleButton from "react-google-button";

import axios from "axios";

const drawerWidth = 100;

const Main = styled("main")(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: drawerWidth / 4,
  backgroundColor: theme.palette.background.default,
}));

const AppBarSpacer = styled("div")(({ theme }) => theme.mixins.toolbar);

// const localBackendUrl = 'http://127.0.0.1:8000'
// const serverBackendUrl = "https://34.95.89.166.nip.io";
// const serverBackendUrl = "https://skillsbot-backend-ap5urm5kva-uc.a.run.app";
const serverBackendUrl = "https://skillsbot-backend-l5ej3633iq-uc.a.run.app";

let idToken = null;
let userEmail = null;
let userName = null;

function App() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [currentTab, setCurrentTab] = useState("Chat");
  const [messages, setMessages] = useState([]);
  const [backendUrl, setBackendUrl] = useState(serverBackendUrl);
  console.info(`----- DEBUG: backendUrl: ${backendUrl}`);

  const [user, setUser] = useState([]);
  const [profile, setProfile] = useState([]);

  const login = useGoogleLogin({
    onSuccess: (codeResponse) => setUser(codeResponse),
    onError: (error) => console.log("Login Failed:", error),
  });

  useEffect(() => {
    if (user) {
      axios
        .get(`https://www.googleapis.com/oauth2/v1/userinfo?access_token=${user.access_token}`, {
          headers: {
            Authorization: `Bearer ${user.access_token}`,
            Accept: "application/json",
          },
        })
        .then((res) => {
          setProfile(res.data);
          idToken = user.access_token;
          userEmail = res.data.email;
          userName = res.data.name;
          console.info(`----- DEBUG: idToken: ${idToken}`);
          console.info(`----- DEBUG: userEmail: ${userEmail}`);
          console.info(`----- DEBUG: userName: ${userName}`);
        })
        .catch((err) => console.log(err));
    }
  }, [user]);

  const handleBackendUrlChange = (event) => {
    // Trim trailing slash if it exists
    if (event.target.value.endsWith("/")) {
      setBackendUrl(event.target.value.slice(0, -1));
    } else {
      setBackendUrl(event.target.value);
    }
  };

  const addMessage = (message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleTabChange = (tab) => {
    setCurrentTab(tab);
  };

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ marginRight: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h4" noWrap component="div" color={"#39FF14"}>
            {/* {currentTab} */}
            Qarik Resume Chatbot
          </Typography>
        </Toolbar>
      </AppBar>
      {drawerOpen && (
        <Drawer
          variant="permanent"
          open={drawerOpen}
          sx={{
            "& .MuiDrawer-paper": {
              position: "relative",
              whiteSpace: "normal",
              width: drawerWidth,
              // backgroundColor: "#424242",
              color: "#ffffff",
            },
          }}
        >
          <AppBarSpacer />
          <List>
            {["Chat", "Resumes", "Settings", "Help"].map((text) => (
              <ListItem button key={text} onClick={() => handleTabChange(text)}>
                <ListItemText primary={text} />
              </ListItem>
            ))}
          </List>
        </Drawer>
      )}

      <Main>
        <AppBarSpacer />
        {!idToken && <GoogleButton onClick={() => login()} />}
        {idToken && (
          <Box
            sx={{
              width: "100%", // Customize the chat box width here (e.g., '80%', '1200px')
              flexGrow: 1,
              flexDirection: "column",
              // height: '100vh',
              // height: "90%", // Customize the chat box height here (e.g., '300px', '600px')
              // padding: (theme) => theme.spacing(1),
              // marginLeft: (theme) => theme.spacing(1),
              // marginRight: (theme) => theme.spacing(1),
              // marginTop: (theme) => theme.spacing(1),
            }}
          >
            {currentTab === "Chat" && <Chat messages={messages} addMessage={addMessage} backendUrl={backendUrl} />}
          </Box>
        )}
        <Box
          sx={{
            width: "100%", // Customize the chat box width here (e.g., '80%', '1200px')
            // height: "90%", // Customize the chat box height here (e.g., '300px', '600px')
            // flexGrow: 1,
            // padding: (theme) => theme.spacing(1),
            // marginLeft: (theme) => theme.spacing(1),
            // marginRight: (theme) => theme.spacing(1),
            // marginTop: (theme) => theme.spacing(1),
          }}
        >
          {currentTab === "Settings" && (
            <Box>
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  // border: "1px solid #555",
                  // borderRadius: "4px",
                  padding: "16px",
                  minHeight: "400px",
                  // backgroundColor: "#333",
                  marginBottom: "16px",
                  overflowY: "auto",
                }}
              >
                <Typography variant="h5">System information</Typography>
                <Typography height={30}></Typography>
                <Typography>
                  <b>Version:</b> 0.1.10
                </Typography>
                <Typography>
                  <b>Software update:</b> June 6, 2023
                </Typography>
                <Typography>
                  <b>Author:</b> Roman Kharkovski (rkharkovski@gmail.com)
                </Typography>
                <Typography>
                  <b>Home page:</b> <a href="go/skills-bot">go/skills-bot</a>
                </Typography>
                <Typography>
                  <b>Source code:</b> <a href="https://github.com/Qarik-Group/skills-bot">GitHub repo</a>
                </Typography>
                <Typography height={50}></Typography>
                <TextField
                  label="Backend REST API URL"
                  value={backendUrl}
                  onChange={handleBackendUrlChange}
                  fullWidth
                  autoFocus
                />
                <Typography fontSize={11} color={"grey"}>
                  Feel free to play with the REST API directly by using the URL above, or change the URL to point to
                  your development instance.
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
        <Box
          sx={{
            width: "100%",
          }}
        >
          {currentTab === "Help" && <Help />}
        </Box>
        {idToken && (
          <Box
            sx={{
              width: "100%",
            }}
          >
            {currentTab === "Resumes" && <Resumes backendUrl={backendUrl} />}
          </Box>
        )}
      </Main>
    </Box>
  );
}

function Chat({ messages, addMessage, backendUrl }) {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (event) => {
    setQuestion(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    addMessage({ sender: userName, text: question });

    try {
      const response = await fetch(`${backendUrl}/ask`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
          Accept: "application/json",
        },
        body: JSON.stringify({ user_id: userEmail, question: question }),
      });

      if (response.ok) {
        const data = await response.json();
        const answer = data.answer;

        // Add the server's response to the chat history
        addMessage({ sender: "Answer", text: answer });
        addMessage({ sender: ":----------------------------------------", text: "" });
      } else {
        console.error("Error occurred while fetching answer:", response.status);
        setErrorMessage(`Error occurred while fetching answer: ${response}`);
      }
    } catch (error) {
      console.error("Error occurred while fetching answer:", error);
      setErrorMessage(`Error occurred while fetching answer: ${error}`);
    }

    // setQuestion("");
    setIsLoading(false);
  };

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          border: "1px solid #555",
          borderRadius: "4px",
          padding: "16px",
          minHeight: "400px",
          backgroundColor: "#333",
          marginBottom: "16px",
          overflowY: "auto",
        }}
      >
        {messages.map((message, index) => (
          <Typography key={index} variant="body1" gutterBottom>
            <b>{message.sender}:</b> {message.text}
          </Typography>
        ))}
      </Box>
      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          id="question-input"
          label="Ask a question"
          variant="outlined"
          value={question}
          onChange={handleChange}
          sx={{ marginBottom: "16px" }}
          autoFocus
        />
        <Button type="submit" variant="contained" color="primary">
          Send
        </Button>
      </form>
      {isLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">LLM processing in progress...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {errorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {errorMessage}
        </Alert>
      )}
      <Typography height={15}></Typography>
      <Typography fontSize={11} color={"grey"}>
        This is an experimental product and is prone to hallucinations and errors. Use at your own risk.
      </Typography>
    </Box>
  );
}

function Help() {
  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          padding: "16px",
          minHeight: "400px",
          marginBottom: "16px",
          overflowY: "auto",
        }}
      >
        <Typography variant="h5">Access and security</Typography>
        <Typography height={15}></Typography>
        <Typography>
          The skills bot is available at <a href="go/skills-bot">go/skills-bot</a> to anyone who can authenticate to
          Google with the company domain id. The frontend web UI and backend REST APIs are protected by Google Identity
          Aware Proxy. Nobody outside of Qarik can access the bot or the data.
        </Typography>
        <Typography height={15}></Typography>
        <Typography variant="h5">How do I use this tool?</Typography>
        <Typography height={15}></Typography>
        <Typography>
          On the <a href="/Chat">Chat</a> tab, enter your query in plain English and press Enter. The bot will attempt
          to answer your query, and augment it's answers using the uploaded resumes of Qarik staff. You can ask
          questions about a single person, or questions about multiple people. The questions about many people take much
          longer (see the explanation below) and currently fail very often, or provide inaccurate results.
        </Typography>
        <Typography height={15}></Typography>
        <Typography variant="h6">Single person queries:</Typography>
        <Typography>- Tell me about [Person Name] strengths and weaknesses?</Typography>
        <Typography>- How long did [Person Name] work for [Company Name]?</Typography>
        <Typography>- Does [Person Name] have experience with AI/ML?</Typography>
        <Typography height={15}></Typography>
        <Typography variant="h6">Multiple people queries (these often fail):</Typography>
        <Typography>- Compare skills of [Person1] and [Person2].</Typography>
        <Typography>- List all people who have Python and data science skills.</Typography>
        <Typography>- Did anybody work for or with Qarik or Google?</Typography>
        <Typography>- What is the most common skill among all people who provided their resume?</Typography>
        <Typography>- Among all people, who has the most experience with Java and Kubernetes?</Typography>
        <Typography>- How many people have skills in Python and Machine Learning?</Typography>
        <Typography height={50}></Typography>
        <Typography variant="h5">How does this app work?</Typography>
        <Typography height={15}></Typography>
        <Typography>
          The application is hosted on GCP as Cloud Run service. Resumes of multiple people uploaded in PDF format to
          the server (currently just keeping a local copy inside of the docker image, but really needs to be on Drive or
          GCS). The backend is built using Python and FastAPI. The bot uses OpenAI's LLM (Language Model) to generate
          answers to your queries. The bot also uses LlamaIndex framework with LangChain to extract data from resumes
          uploaded into the system.
        </Typography>
        <Typography>
          The reason the system is so slow for queries across multiple resumes, is that LlamaIndex runs a separate query
          for each resume, and then combines the results. All this is done serially, with no parallelism. As the number
          of resumes increases, this approach will not scale. It is not clear if LlamaIndex plans to address this issue
          in the future, or I need to be using it differently.
        </Typography>
        <Typography height={50}></Typography>
        <Typography variant="h5">How do I submit feature requests and file bugs?</Typography>
        <Typography height={15}></Typography>
        <Typography>
          If you found a bug, or have any ideas on how to improve this tool, please open an issue using project's
          <a href="https://github.com/Qarik-Group/resume-chatbot/issues">GitHub Issues</a> page.
        </Typography>
      </Box>
    </Box>
  );
}

function Resumes({ backendUrl }) {
  const [peopleList, setPeopleList] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function fetchPeopleList() {
    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/people`, {
        method: "GET",
        credentials: "include",
        // mode: "no-cors",
        headers: {
          Authorization: `Bearer ${idToken}`,
          Accept: "application/json, text/plain, */*",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": true,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPeopleList(data);
      } else {
        console.error("Error occurred while loading list of resumes:", response.status);
        setErrorMessage(`Error occurred while loading list of resumes: ${response.status}`);
      }
    } catch (error) {
      console.error("Error occurred while fetching answer:", error);
      setErrorMessage(`Error occurred while fetching answer: ${error}`);
    }
    setIsLoading(false);
  }

  useEffect(() => {
    fetchPeopleList();
  }, []); // Pass an empty array to run the effect only on mount

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        padding: "16px",
        minHeight: "400px",
        marginBottom: "16px",
        overflowY: "auto",
      }}
    >
      <Typography variant="h5">What resumes are available for queries?</Typography>
      {isLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">Getting list of resumes from the server...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {errorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {errorMessage}
        </Alert>
      )}
      <List>
        {peopleList.map((string, index) => (
          <ListItem key={index} sx={{ paddingTop: "1px", paddingBottom: "1px" }}>
            <ListItemText primary={`${index + 1}. ${string}`} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

export default App;
