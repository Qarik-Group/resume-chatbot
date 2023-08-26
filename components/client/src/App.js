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
import { BarElement, BarController, Chart, CategoryScale, LinearScale } from "chart.js";
import { Bar } from "react-chartjs-2";

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
  Checkbox,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { styled } from "@mui/system";
import { CircularProgress } from "@mui/material";
import { useGoogleLogin } from "@react-oauth/google";
import GoogleButton from "react-google-button";
import "./App.css";

import axios from "axios";

const drawerWidth = 100;

const Main = styled("main")(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: drawerWidth / 4,
  backgroundColor: theme.palette.background.default,
}));

const AppBarSpacer = styled("div")(({ theme }) => theme.mixins.toolbar);

// eslint-disable-next-line no-unused-vars
const localHostBackend = "http://127.0.0.1:5002";
// eslint-disable-next-line no-unused-vars
const cloudRunBackendProtectedIAP = "https://skillsbot-backend-ap5urm5kva-uc.a.run.app";
// eslint-disable-next-line no-unused-vars
const cloudRunBackendDev = "https://skillsbot-backend-l5ej3633iq-uc.a.run.app";
// eslint-disable-next-line no-unused-vars
const iapBackend = "https://34.95.89.166.nip.io";
// Which backend URL to use as the default value
const defaultBackendUrl = iapBackend;

// User name to display in the chat window
let userName = null;
const fakeIdToken = "fakeIdToken";

// Current voting stats for all different LLM engines
let llmVotingStats = null;

// Which LLM engines to use
let useGoogLlm = true;
let usePalmLlm = true;
let useGptLlm = true;
let useVertexLlm = true;

Chart.register(CategoryScale, LinearScale, BarElement, BarController);

const ChartComponent = ({ data }) => {
  // Extracting data from the provided prop
  const names = data.map((item) => item.name);
  const upVotes = data.map((item) => item.up);
  const downVotes = data.map((item) => item.down);

  const chartData = {
    labels: names,
    datasets: [
      {
        label: "Upvotes",
        data: upVotes,
        backgroundColor: "#39ff15", // You can customize this color
        borderWidth: 1,
      },
      {
        label: "Downvotes",
        data: downVotes,
        backgroundColor: "#d83f3f", // You can customize this color
        borderWidth: 1,
      },
    ],
  };

  return (
    <div>
      <Bar
        data={chartData}
        options={{
          responsive: true,
          scales: {
            y: {
              beginAtZero: false,
              stacked: true, // Enable this for stacking
            },
            x: {
              stacked: true, // Enable this for stacking
            },
          },
        }}
      />
    </div>
  );
};

function App() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [currentTab, setCurrentTab] = useState("Chat");
  const [messages, setMessages] = useState([]);
  const [backendUrl, setBackendUrl] = useState(defaultBackendUrl);
  const [idToken, setIdToken] = useState(null);
  const [user, setUser] = useState([]);

  // Whether or not use particular LLM engine
  const [useGoog, setGoogLlm] = useState(useGoogLlm);
  const [usePalm, setPalmLlm] = useState(usePalmLlm);
  const [useGpt, setGptLlm] = useState(useGptLlm);
  const [useVertex, setVertexLlm] = useState(useVertexLlm);

  const login = useGoogleLogin({
    onSuccess: (codeResponse) => setUser(codeResponse),
    onError: (error) => console.log("Login Failed:", error),
  });

  console.info(`DEBUG: backendUrl: ${backendUrl}, idToken: ${idToken}`);

  useEffect(() => {
    useGoogLlm = useGoog;
  }, [useGoog]);

  useEffect(() => {
    usePalmLlm = usePalm;
  }, [usePalm]);

  useEffect(() => {
    useVertexLlm = useVertex;
  }, [useVertex]);

  useEffect(() => {
    useGptLlm = useGpt;
  }, [useGpt]);

  useEffect(() => {
    // If query engine is running locally or on unprotected Cloud Run, then use fake ID token and ignore user Auth
    if (backendUrl.includes("127.0.0.1") || backendUrl.includes("localhost") || backendUrl.includes(".run.app")) {
      setIdToken(fakeIdToken);
      userName = "Test User";
      console.info(`DEBUG: updating idToken to fakeIdToken: ${idToken}`);
    }
    // eslint-disable-next-line
  }, [backendUrl]);

  useEffect(() => {
    if (user && idToken !== fakeIdToken) {
      axios
        .get(`https://www.googleapis.com/oauth2/v1/userinfo?access_token=${user.access_token}`, {
          headers: {
            Authorization: `Bearer ${user.access_token}`,
            Accept: "application/json",
          },
        })
        .then((res) => {
          setIdToken(user.access_token);
          userName = res.data.name;
          console.info(`DEBUG: userName: ${userName}`);
        })
        .catch((err) => console.log(err));
    }
    // eslint-disable-next-line
  }, [user]);

  const handleBackendUrlChange = (event) => {
    if (event.target.value.endsWith("/")) {
      setBackendUrl(event.target.value.slice(0, -1));
    } else {
      setBackendUrl(event.target.value);
    }
    if (idToken === fakeIdToken) {
      setIdToken(null);
    }
  };

  function addMessage(role, sender, text) {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: role,
        sender: sender,
        text: text,
        upvoted: false,
        downvoted: false,
      },
    ]);
  }

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
              color: "#ffffff",
            },
          }}
        >
          <AppBarSpacer />
          <List>
            {["Chat", "Resumes", "Config", "Stats", "Help"].map((text) => (
              <ListItem button key={text} onClick={() => handleTabChange(text)}>
                <ListItemText primary={text} />
              </ListItem>
            ))}
          </List>
        </Drawer>
      )}

      <Main>
        <AppBarSpacer />
        {!idToken && (currentTab === "Chat" || currentTab === "Resumes") && <GoogleButton onClick={() => login()} />}
        {idToken && (
          <Box
            sx={{
              width: "100%",
              flexGrow: 1,
              flexDirection: "column",
            }}
          >
            {currentTab === "Chat" && (
              <Chat messages={messages} addMessage={addMessage} backendUrl={backendUrl} idToken={idToken} />
            )}
          </Box>
        )}
        <Box sx={{ width: "100%" }}>
          {currentTab === "Config" && (
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
                <Typography variant="h3">Config</Typography>
                <Typography height={15}></Typography>
                <Typography>
                  <Checkbox
                    checked={useGoog}
                    onChange={(e) => setGoogLlm(e.target.checked)}
                    inputProps={{ "aria-label": "controlled" }}
                  />
                  use Google Enterprise Search with summarization (API hosted by Google Gen AI in this GCP project)
                </Typography>
                <Typography>
                  <Checkbox
                    checked={useGpt}
                    onChange={(e) => setGptLlm(e.target.checked)}
                    inputProps={{ "aria-label": "controlled" }}
                  />
                  use Chat GPT 4.0 via Llama-Index (public API hosted by OpenAI)
                </Typography>
                <Typography>
                  <Checkbox
                    checked={usePalm}
                    onChange={(e) => setPalmLlm(e.target.checked)}
                    inputProps={{ "aria-label": "controlled" }}
                  />
                  use Google PaLM via Llama-Index (public API hosted by Google)
                </Typography>
                <Typography>
                  <Checkbox
                    checked={useVertex}
                    onChange={(e) => setVertexLlm(e.target.checked)}
                    inputProps={{ "aria-label": "controlled" }}
                  />
                  use Google Vertex AI Bison LLM via Langchain (hosted in this project)
                </Typography>
                <Typography height={20}></Typography>
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
        <Box sx={{ width: "80%", height: "80%" }}>
          {currentTab === "Stats" && (
            <Box>
              <Typography variant="h3">Voting results</Typography>
              <Typography height={15}></Typography>
              {llmVotingStats && (
                <div>
                  <Typography>Aggregated user votes for the accuracy of responses.</Typography>
                  <ChartComponent data={llmVotingStats}/>
                </div>
              )}
              {!llmVotingStats && (
                <Typography>You must vote on at least one answer in order to see voting results.</Typography>
              )}
            </Box>
          )}
        </Box>
        <Box sx={{ width: "100%" }}>{currentTab === "Help" && <Help />}</Box>
        {idToken && (
          <Box sx={{ width: "100%" }}>
            {currentTab === "Resumes" && <Resumes backendUrl={backendUrl} idToken={idToken} />}
          </Box>
        )}
      </Main>
    </Box>
  );
}

function Chat({ messages, addMessage, backendUrl, idToken }) {
  const [question, setQuestion] = useState("");

  // Loading indicators for various LLM engines
  const [isGptLoading, setIsGptLoading] = useState(false);
  const [isPalmLoading, setIsPalmLoading] = useState(false);
  const [isGoogLoading, setIsGoogLoading] = useState(false);
  const [isVertexLoading, setIsVertexLoading] = useState(false);

  // Error messages from various LLM engines
  const [gptErrorMessage, setGptErrorMessage] = useState("");
  const [palmErrorMessage, setPalmErrorMessage] = useState("");
  const [googErrorMessage, setGoogErrorMessage] = useState("");
  const [vertexErrorMessage, setVertexErrorMessage] = useState("");

  // Prefixes for the answers from various LLM engines
  const answerPrefixGpt = "Chat GPT";
  const answerPrefixPalm = "Google PaLM";
  const answerPrefixGoog = "Google GenAI";
  const answerPrefixVertex = "Google VertexAI Bison";

  // Which LLM engines to use

  const handleChange = (event) => {
    setQuestion(event.target.value);
  };

  const callBackendLlm = async (event, url, errorHandler, answerPrefix, isLoading) => {
    event.preventDefault();
    try {
      errorHandler("");
      isLoading(true);
      const response = await fetch(url, {
        method: "POST",
        credentials: idToken === fakeIdToken ? "omit" : "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
          Accept: "application/json, text/plain, */*",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": true,
        },
        body: JSON.stringify({ question: question }),
      });

      isLoading(false);
      if (response.ok) {
        const data = await response.json();
        const answer = data.answer;
        // Add the server's response to the chat history
        addMessage("server", answerPrefix, answer);
      } else {
        const contentType = response.headers.get("Content-Type");
        let error;
        if (contentType && contentType.includes("application/json")) {
          error = JSON.stringify(await response.json());
        } else {
          error = await response.text();
        }
        console.error(`Error from: ${url}, status: ${response.status}, error: ${error}`);
        errorHandler(`Error from: ${url}, status: ${response.status}, error: ${error}`);
      }
    } catch (error) {
      isLoading(false);
      console.error(`Error calling: ${url}, error: ${error}`);
      errorHandler(`Error calling: ${url}, error: ${error}`);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    addMessage("user", userName, question);
    if (useGptLlm) {
      callBackendLlm(event, `${backendUrl}/ask_gpt`, setGptErrorMessage, answerPrefixGpt, setIsGptLoading);
    }
    if (usePalmLlm) {
      callBackendLlm(event, `${backendUrl}/ask_palm`, setPalmErrorMessage, answerPrefixPalm, setIsPalmLoading);
    }
    if (useVertexLlm) {
      callBackendLlm(event, `${backendUrl}/ask_vertex`, setVertexErrorMessage, answerPrefixVertex, setIsVertexLoading);
    }
    if (useGoogLlm) {
      callBackendLlm(event, `${backendUrl}/ask_google`, setGoogErrorMessage, answerPrefixGoog, setIsGoogLoading);
    }
    // Reset the question field to be empty - or comment this out to leave it with the previous question
    // setQuestion("");
  };

  const [showVoteResultMessageSuccess, setShowVoteResultMessageSuccess] = useState(false);
  const [showVoteResultMessageError, setShowVoteResultMessageError] = useState(false);

  const displayVoteResultMessageSuccess = () => {
    setShowVoteResultMessageSuccess(true);
    setTimeout(() => {
      setShowVoteResultMessageSuccess(false);
    }, 1000); // fade out after 1 second
  };

  const displayVoteResultMessageError = () => {
    setShowVoteResultMessageError(true);
    setTimeout(() => {
      setShowVoteResultMessageError(false);
    }, 1000); // fade out after 1 second
  };

  const callBackendVote = async (message, index) => {
    const url = `${backendUrl}/vote`;
    // Loop back in 'messages' until we find the role of user question
    let user_index = index - 1;
    while (user_index > 0 && messages[user_index].role !== "user") {
      user_index--;
    }
    const question = messages[user_index].text;
    // const question = messages[index].text;
    try {
      const response = await fetch(url, {
        method: "POST",
        credentials: idToken === fakeIdToken ? "omit" : "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
          Accept: "application/json, text/plain, */*",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": true,
        },
        // body: JSON.stringify(message),
        body: JSON.stringify({
          llm_backend: message.sender,
          question: question,
          answer: message.text,
          upvoted: message.upvoted,
          downvoted: message.downvoted,
        }),
      });

      if (response.ok) {
        llmVotingStats = await response.json();
        console.info(`DEBUG: llmStats: ${JSON.stringify(llmVotingStats)}`);
        displayVoteResultMessageSuccess();
      } else {
        displayVoteResultMessageError();
        const contentType = response.headers.get("Content-Type");
        let error;
        if (contentType && contentType.includes("application/json")) {
          error = JSON.stringify(await response.json());
        } else {
          error = await response.text();
        }
        console.error(`Error from: ${url}, status: ${response.status}, error: ${error}`);
      }
    } catch (error) {
      console.error(`Error calling: ${url}, error: ${error}`);
    }
  };

  function handleUpvote(index) {
    const updatedMessages = [...messages];
    if (!updatedMessages[index].upvoted) {
      updatedMessages[index].upvoted = true;
      updatedMessages[index].downvoted = false;
      console.info(`DEBUG: upvoted message: ${JSON.stringify(updatedMessages[index])}`);
      callBackendVote(updatedMessages[index], index);
    }
  }

  function handleDownvote(index) {
    const updatedMessages = [...messages];
    if (!updatedMessages[index].downvoted) {
      updatedMessages[index].downvoted = true;
      updatedMessages[index].upvoted = false;
      console.info(`DEBUG: upvoted message: ${JSON.stringify(updatedMessages[index])}`);
      callBackendVote(updatedMessages[index], index);
    }
  }

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
          <div key={index} className={`message ${message.role.toLowerCase()}`}>
            <span className="prefix">{message.sender}</span>: {message.text}
            {message.role === "server" && (
              <span className="feedback-icons">
                <span onClick={() => handleUpvote(index)}> 👍</span>
                <span onClick={() => handleDownvote(index)}>👎</span>
              </span>
            )}
          </div>
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
      {isGptLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">Processing request for ChatGPT...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {isPalmLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">Processing request for Google PaLM...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {isGoogLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">Processing request for Google Gen AI...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {isVertexLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50px",
          }}
        >
          <Typography variant="body1">Processing request for Google VertexAX Bison...</Typography>
          <CircularProgress sx={{ marginRight: "8px" }} />
        </Box>
      )}
      {gptErrorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {gptErrorMessage}
        </Alert>
      )}
      {palmErrorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {palmErrorMessage}
        </Alert>
      )}
      {googErrorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {googErrorMessage}
        </Alert>
      )}
      {vertexErrorMessage && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {vertexErrorMessage}
        </Alert>
      )}
      <Typography height={15}></Typography>
      <Typography fontSize={11} color={"grey"}>
        This is an experimental product and is prone to hallucinations and errors. Use at your own risk.
      </Typography>
      <Typography>
        <div className={showVoteResultMessageSuccess ? "fade-message-success active" : "fade-message-success"}>
          Your vote has been registered.
        </div>
        <div className={showVoteResultMessageError ? "fade-message-error active" : "fade-message-error"}>
          Error registering your vote. Something may be wrong with the server.
        </div>
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
        <Typography variant="h3">Help and system information</Typography>
        <Typography height={15}></Typography>
        <Typography>Client version: 0.1.18</Typography>
        <Typography>Software update: August 25, 2023</Typography>
        <Typography>Author: Roman Kharkovski (kharkovski@gmail.com)</Typography>
        <Typography>
          Source code: <a href="https://github.com/Qarik-Group/resume-chatbot">GitHub repo</a>
        </Typography>
        <Typography height={15}></Typography>
        <Typography variant="h4">Access and security</Typography>
        <Typography height={15}></Typography>
        <Typography>
          Production instance available for Qarik employees with corporate SSO login:{" "}
          <a href="https://go.qarik.com/skills-bot">go/skills-bot</a>. The frontend web UI and backend REST APIs are
          protected by Google Identity Aware Proxy. Nobody outside of Qarik can access the bot or the data.
        </Typography>
        <Typography height={15}></Typography>
        <Typography variant="h4">How do I use this tool?</Typography>
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
        <Typography height={15}></Typography>
        <Typography variant="h4">How does this app work?</Typography>
        <Typography height={15}></Typography>
        <Typography>
          The application is hosted on GCP as Cloud Run service. Resumes of multiple people uploaded in PDF format to
          the GCS bucket and can be updated at any time. The backend is built using Python and FastAPI. The chat bot
          uses several different LLM implementations (ChatGPT API, Google PaLM, Google Enterprise Search, and Google
          VertexAI Bison) to generate answers to your queries. The bot also uses LlamaIndex framework with LangChain to
          extract data from resumes uploaded into the system.
        </Typography>
        <Typography height={15}></Typography>
        <Typography variant="h4">How do I submit feature requests and file bugs?</Typography>
        <Typography height={15}></Typography>
        <Typography>
          If you found a bug, or have any ideas for improvement, please open an issue using project's{" "}
          <a href="https://github.com/Qarik-Group/resume-chatbot/issues">GitHub Issues</a> page.
        </Typography>
      </Box>
    </Box>
  );
}

function Resumes({ backendUrl, idToken }) {
  const [peopleList, setPeopleList] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function fetchPeopleList() {
    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/people`, {
        method: "GET",
        credentials: idToken === fakeIdToken ? "omit" : "include",
        headers: {
          Authorization: `Bearer ${idToken}`,
          // Accept: "application/json",
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
    // eslint-disable-next-line
  }, []);

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
      <Typography variant="h4">List of resumes available for queries</Typography>
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
