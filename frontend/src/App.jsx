import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [page, setPage] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [skills, setSkills] = useState("");

  const [project, setProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);

  const [progress, setProgress] = useState(0);
  const [completedTasks, setCompletedTasks] = useState(0);
  const [pendingTasks, setPendingTasks] = useState(0);

  const [analysis, setAnalysis] = useState("");

  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState([]);

  const [loading, setLoading] = useState(false);

  const API = "https://scientists-highlights-strike-manually.trycloudflare.com";


  // ==========================================
  // AUTH HEADER
  // ==========================================

  const authHeaders = () => {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };
  };


  // ==========================================
  // LOGIN
  // ==========================================

  const login = async () => {
    if (!email || !password) {
      alert("Please enter email and password");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Login failed");
        return;
      }

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("user_name", data.name);

      setName(data.name);

      // Load all user projects
      await loadProjects();

      setPage("projects");

    } catch (error) {
      alert("Backend connection failed");
    } finally {
      setLoading(false);
    }
  };


  // ==========================================
  // REGISTER
  // ==========================================

  const register = async () => {
    if (!name || !email || !password) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name,
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Registration failed");
        return;
      }

      alert("Registration successful! Please login.");

      setPage("login");
      setPassword("");

    } catch (error) {
      alert("Backend connection failed");
    } finally {
      setLoading(false);
    }
  };


  // ==========================================
  // LOAD ALL USER PROJECTS
  // ==========================================

  const loadProjects = async () => {
    try {
      const response = await fetch(
        `${API}/projects/my-projects`,
        {
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Failed to load projects");
        return;
      }

      setProjects(data);

    } catch (error) {
      alert("Backend connection failed");
    }
  };


  // ==========================================
  // OPEN PROJECT
  // ==========================================

  const openProject = async (selectedProject) => {

    setProject(selectedProject);

    setAnalysis("");

    setChatMessages([]);

    await loadTasks(selectedProject.id);

    await analyzeProgress(selectedProject.id);

    setPage("dashboard");
  };


  // ==========================================
  // CREATE PROJECT
  // ==========================================

  const createProject = async () => {

    if (!projectName || !description || !skills) {
      alert("Please fill all project details");
      return;
    }

    try {

      const response = await fetch(
        `${API}/projects/create`,
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({
            user_id: Number(
              localStorage.getItem("user_id")
            ),
            name: projectName,
            description: description,
            skills: skills,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
          "Project creation failed"
        );
        return;
      }

      alert(
        `Project created successfully!\n${data.tasks_created} roadmap tasks created.`
      );


      const newProject = {
        id: data.project_id,
        name: data.project_name,
        description: description,
        skills: skills,
        total_tasks: data.tasks_created,
        completed_tasks: 0,
        pending_tasks: data.tasks_created,
        progress: 0,
      };


      // Add project to projects list
      setProjects((previous) => [
        newProject,
        ...previous,
      ]);


      setProject(newProject);

      setProjectName("");
      setDescription("");
      setSkills("");

      await loadTasks(data.project_id);

      await analyzeProgress(data.project_id);

      setPage("dashboard");

    } catch (error) {

      alert("Backend connection failed");

    }
  };


  // ==========================================
  // LOAD TASKS
  // ==========================================

  const loadTasks = async (projectId) => {

    try {

      const response = await fetch(
        `${API}/projects/tasks/${projectId}`,
        {
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setTasks(data);
      }

    } catch (error) {

      console.log(error);

    }
  };


  // ==========================================
  // ANALYZE PROJECT
  // ==========================================

  const analyzeProject = async () => {

    if (!project) {
      return;
    }

    try {

      const response = await fetch(
        `${API}/projects/analyze/${project.id}`,
        {
          method: "POST",
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setAnalysis(data.analysis);
      }

    } catch (error) {

      console.log(error);

    }
  };


  // ==========================================
  // ANALYZE PROGRESS
  // ==========================================

  const analyzeProgress = async (projectId) => {

    try {

      const response = await fetch(
        `${API}/projects/progress/${projectId}`,
        {
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (response.ok) {

        setProgress(data.progress);

        setCompletedTasks(
          data.completed_tasks
        );

        setPendingTasks(
          data.pending_tasks
        );

      }

    } catch (error) {

      console.log(error);

    }
  };


  // ==========================================
  // COMPLETE TASK
  // ==========================================

  const completeTask = async (taskId) => {

    try {

      const response = await fetch(
        `${API}/projects/tasks/${taskId}?status=Completed`,
        {
          method: "PUT",
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {

        alert(
          data.detail ||
          "Task update failed"
        );

        return;
      }


      await loadTasks(project.id);

      await analyzeProgress(project.id);

      // Refresh project list
      await loadProjects();

    } catch (error) {

      alert("Backend connection failed");

    }
  };


  // ==========================================
  // CHATBOT
  // ==========================================

  const sendMessage = async () => {

    if (!message.trim() || !project) {
      return;
    }

    const userMessage = message;

    setMessage("");


    setChatMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: userMessage,
      },
    ]);


    try {

      const response = await fetch(
        `${API}/projects/chat`,
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({
            project_id: project.id,
            message: userMessage,
          }),
        }
      );


      const data = await response.json();


      if (!response.ok) {

        alert(
          data.detail ||
          "Chat failed"
        );

        return;
      }


      setChatMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: data.ai_response,
        },
      ]);

    } catch (error) {

      alert("Backend connection failed");

    }
  };


  // ==========================================
  // PHASE
  // ==========================================

  const getPhase = (title) => {

    if (
      title === "Requirement Analysis" ||
      title === "System Design"
    ) {
      return "Phase 1 — Planning";
    }


    if (title === "Database Design") {
      return "Phase 2 — Database";
    }


    if (
      title === "Backend Development" ||
      title === "Frontend Development" ||
      title === "Feature Implementation"
    ) {
      return "Phase 3 — Development";
    }


    if (
      title === "Testing" ||
      title === "Bug Fixing"
    ) {
      return "Phase 4 — Testing";
    }


    return "Phase 5 — Finalization";
  };


  // ==========================================
  // GROUP TASKS
  // ==========================================

  const groupedTasks = tasks.reduce(
    (groups, task) => {

      const phase = getPhase(
        task.title
      );


      if (!groups[phase]) {
        groups[phase] = [];
      }


      groups[phase].push(task);


      return groups;

    },
    {}
  );


  // ==========================================
  // CHECK LOGIN ON PAGE LOAD
  // ==========================================

  useEffect(() => {

    const token =
      localStorage.getItem("token");


    if (token) {

      setName(
        localStorage.getItem(
          "user_name"
        ) || ""
      );

      loadProjects();

      setPage("projects");

    }

  }, []);


  // ==========================================
  // LOGIN PAGE
  // ==========================================

  if (page === "login") {

    return (

      <div className="auth-page">

        <div className="auth-card">

          <h1>
            🤖 AI Project Mentor
          </h1>

          <p className="subtitle">
            Smart Project Development Assistant
          </p>


          <h2>
            Login
          </h2>


          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />


          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />


          <button
            onClick={login}
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>


          <p>
            Don't have an account?
          </p>


          <button
            className="secondary-button"
            onClick={() =>
              setPage("register")
            }
          >
            Create Account
          </button>

        </div>

      </div>

    );
  }


  // ==========================================
  // REGISTER PAGE
  // ==========================================

  if (page === "register") {

    return (

      <div className="auth-page">

        <div className="auth-card">

          <h1>
            🤖 AI Project Mentor
          </h1>


          <h2>
            Create Account
          </h2>


          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) =>
              setName(e.target.value)
            }
          />


          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />


          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />


          <button
            onClick={register}
          >
            {loading
              ? "Creating..."
              : "Register"}
          </button>


          <p>
            Already have an account?
          </p>


          <button
            className="secondary-button"
            onClick={() =>
              setPage("login")
            }
          >
            Back to Login
          </button>

        </div>

      </div>

    );
  }


  // ==========================================
  // MY PROJECTS PAGE
  // ==========================================

  if (page === "projects") {

    return (

      <div className="app-container">

        {/* TOP BAR */}

        <header className="topbar">

          <div>

            <h1>
              🤖 AI Project Mentor
            </h1>

            <span>
              Welcome, {name}
            </span>

          </div>


          <div className="topbar-buttons">

            <button
              onClick={() =>
                setPage("create")
              }
            >
              + New Project
            </button>


            <button
              className="logout-button"
              onClick={() => {

                localStorage.removeItem(
                  "token"
                );

                localStorage.removeItem(
                  "user_id"
                );

                localStorage.removeItem(
                  "user_name"
                );


                setProject(null);
                setProjects([]);
                setTasks([]);
                setChatMessages([]);


                setPage("login");

              }}
            >
              Logout
            </button>

          </div>

        </header>


        {/* PROJECT LIST */}

        <main className="main-content">

          <section className="projects-page">

            <div className="projects-heading">

              <div>

                <p className="small-title">
                  YOUR WORKSPACE
                </p>

                <h2>
                  📁 My Projects
                </h2>

                <p>
                  Select a project to continue
                  your development.
                </p>

              </div>


              <button
                onClick={() =>
                  setPage("create")
                }
              >
                🚀 Create Project
              </button>

            </div>


            {projects.length === 0 ? (

              <div className="welcome-card">

                <h2>
                  No projects yet
                </h2>

                <p>
                  Create your first project
                  to generate an automatic
                  development roadmap.
                </p>


                <button
                  onClick={() =>
                    setPage("create")
                  }
                >
                  🚀 Create My Project
                </button>

              </div>

            ) : (

              <div className="projects-grid">

                {projects.map(
                  (item) => (

                    <div
                      className="project-card"
                      key={item.id}
                    >

                      <div className="project-card-header">

                        <div>

                          <span className="project-icon">
                            📁
                          </span>

                          <h3>
                            {item.name}
                          </h3>

                        </div>

                      </div>


                      <p className="project-description">
                        {item.description}
                      </p>


                      <div className="project-skills">
                        🛠 {item.skills}
                      </div>


                      <div className="project-progress">

                        <div className="progress-label">

                          <span>
                            Progress
                          </span>

                          <strong>
                            {item.progress}%
                          </strong>

                        </div>


                        <div className="progress-bar">

                          <div
                            className="progress-fill"
                            style={{
                              width:
                                `${item.progress}%`,
                            }}
                          ></div>

                        </div>

                      </div>


                      <div className="project-stats">

                        <span>
                          ✅ {item.completed_tasks}
                          {" "}Completed
                        </span>

                        <span>
                          ⏳ {item.pending_tasks}
                          {" "}Pending
                        </span>

                      </div>


                      <button
                        className="open-project-button"
                        onClick={() =>
                          openProject(item)
                        }
                      >
                        Open Project →
                      </button>

                    </div>

                  )
                )}

              </div>

            )}

          </section>

        </main>

      </div>

    );
  }


  // ==========================================
  // CREATE PROJECT PAGE
  // ==========================================

  if (page === "create") {

    return (

      <div className="app-container">

        <header className="topbar">

          <div>

            <h1>
              🤖 AI Project Mentor
            </h1>

          </div>


          <button
            className="logout-button"
            onClick={() =>
              setPage("projects")
            }
          >
            Back
          </button>

        </header>


        <main className="main-content">

          <div className="create-card">

            <h2>
              🚀 Create Your Project
            </h2>


            <p>
              Enter your project details and
              the system will automatically
              generate a roadmap.
            </p>


            <label>
              Project Name
            </label>


            <input
              type="text"
              placeholder="Enter project name"
              value={projectName}
              onChange={(e) =>
                setProjectName(e.target.value)
              }
            />


            <label>
              Project Description
            </label>


            <textarea
              placeholder="Describe your project"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
            />


            <label>
              Skills / Technologies
            </label>


            <input
              type="text"
              placeholder="Example: Python, React, PostgreSQL"
              value={skills}
              onChange={(e) =>
                setSkills(e.target.value)
              }
            />


            <button
              onClick={createProject}
            >
              🚀 Create Project
            </button>

          </div>

        </main>

      </div>

    );
  }


  // ==========================================
  // DASHBOARD
  // ==========================================

  return (

    <div className="app-container">

      {/* TOP BAR */}

      <header className="topbar">

        <div>

          <h1>
            🤖 AI Project Mentor
          </h1>

          <span>
            Welcome, {name}
          </span>

        </div>


        <div className="topbar-buttons">

          <button
            onClick={() =>
              setPage("projects")
            }
          >
            📁 My Projects
          </button>


          <button
            onClick={() =>
              setPage("create")
            }
          >
            + New Project
          </button>


          <button
            className="logout-button"
            onClick={() => {

              localStorage.removeItem(
                "token"
              );

              localStorage.removeItem(
                "user_id"
              );

              localStorage.removeItem(
                "user_name"
              );


              setProject(null);
              setProjects([]);
              setTasks([]);
              setChatMessages([]);


              setPage("login");

            }}
          >
            Logout
          </button>

        </div>

      </header>


      {/* MAIN */}

      <main className="main-content">

        {!project ? (

          <div className="welcome-card">

            <h2>
              Welcome to your AI Project
              Mentor 👋
            </h2>


            <p>
              Create your first project
              to generate an automatic
              development roadmap.
            </p>


            <button
              onClick={() =>
                setPage("create")
              }
            >
              🚀 Create My Project
            </button>

          </div>

        ) : (

          <>

            {/* PROJECT HEADER */}

            <section className="project-header">

              <div>

                <p className="small-title">
                  CURRENT PROJECT
                </p>


                <h2>
                  {project.name}
                </h2>


                <p>
                  {project.description}
                </p>


                <span className="skills">
                  🛠 {project.skills}
                </span>

              </div>


              <button
                onClick={analyzeProject}
              >
                🤖 Analyze Project
              </button>

            </section>


            {/* STAT CARDS */}

            <section className="stats-grid">

              <div className="stat-card">

                <span>
                  📊
                </span>

                <h3>
                  {progress}%
                </h3>

                <p>
                  Overall Progress
                </p>

              </div>


              <div className="stat-card">

                <span>
                  ✅
                </span>

                <h3>
                  {completedTasks}
                </h3>

                <p>
                  Completed Tasks
                </p>

              </div>


              <div className="stat-card">

                <span>
                  ⏳
                </span>

                <h3>
                  {pendingTasks}
                </h3>

                <p>
                  Pending Tasks
                </p>

              </div>


              <div className="stat-card">

                <span>
                  📋
                </span>

                <h3>
                  {tasks.length}
                </h3>

                <p>
                  Total Tasks
                </p>

              </div>

            </section>


            {/* PROGRESS */}

            <section className="dashboard-card">

              <div className="section-title">

                <h2>
                  📈 Project Progress
                </h2>


                <strong>
                  {progress}%
                </strong>

              </div>


              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{
                    width:
                      `${progress}%`,
                  }}
                ></div>

              </div>


              <p>
                {completedTasks} of{" "}
                {tasks.length} tasks completed
              </p>

            </section>


            {/* AI ANALYSIS */}

            {analysis && (

              <section className="dashboard-card">

                <h2>
                  🤖 AI Project Analysis
                </h2>


                <pre className="analysis-box">
                  {analysis}
                </pre>

              </section>

            )}


            {/* ROADMAP */}

            <section className="roadmap-section">

              <h2>
                🗺️ Project Roadmap
              </h2>


              {Object.keys(
                groupedTasks
              ).map(

                (phase) => (

                  <div
                    className="phase-card"
                    key={phase}
                  >

                    <h3>
                      {phase}
                    </h3>


                    {groupedTasks[
                      phase
                    ].map(

                      (task) => (

                        <div
                          className="roadmap-task"
                          key={task.id}
                        >

                          <div className="task-info">

                            <h4>

                              {task.status ===
                              "Completed"
                                ? "✅ "
                                : "⏳ "
                              }

                              {task.title}

                            </h4>


                            <p>
                              {task.description}
                            </p>


                            <small>

                              Priority:{" "}

                              <strong>
                                {task.priority}
                              </strong>

                            </small>

                          </div>


                          {task.status !==
                          "Completed" ? (

                            <button
                              onClick={() =>
                                completeTask(
                                  task.id
                                )
                              }
                            >
                              Complete
                            </button>

                          ) : (

                            <span className="completed-label">
                              Completed ✓
                            </span>

                          )}

                        </div>

                      )
                    )}

                  </div>

                )
              )}

            </section>


            {/* CHATBOT */}

            <section className="chatbot-section">

              <h2>
                🤖 AI Project Mentor Chatbot
              </h2>


              <p>
                Ask your mentor about your
                project, progress or next task.
              </p>


              <div className="chat-box">

                {chatMessages.length ===
                  0 && (

                    <div className="chat-welcome">

                      <strong>
                        AI Mentor 👋
                      </strong>


                      <p>
                        Ask me what you should
                        work on next.
                      </p>

                    </div>

                  )}


                {chatMessages.map(
                  (chat, index) => (

                    <div
                      key={index}
                      className={
                        chat.sender === "user"
                          ? "chat-message user-message"
                          : "chat-message ai-message"
                      }
                    >

                      <strong>

                        {chat.sender ===
                        "user"
                          ? "You"
                          : "AI Mentor"
                        }

                      </strong>


                      <pre>
                        {chat.text}
                      </pre>

                    </div>

                  )
                )}

              </div>


              <div className="chat-input">

                <input
                  type="text"
                  placeholder="Ask your AI mentor..."
                  value={message}
                  onChange={(e) =>
                    setMessage(
                      e.target.value
                    )
                  }
                  onKeyDown={(e) => {

                    if (
                      e.key === "Enter"
                    ) {
                      sendMessage();
                    }

                  }}
                />


                <button
                  onClick={sendMessage}
                >
                  Send
                </button>

              </div>

            </section>

          </>

        )}

      </main>

    </div>

  );
}

export default App;