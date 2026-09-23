from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Project, ChatHistory, Task

router = APIRouter()


# ==========================================
# DATABASE
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# REQUEST MODELS
# ==========================================

class ProjectRequest(BaseModel):
    user_id: int
    name: str
    description: str
    skills: str


class ChatRequest(BaseModel):
    project_id: int
    message: str


class TaskRequest(BaseModel):
    project_id: int
    title: str
    description: str = ""
    priority: str = "Medium"


# ==========================================
# ROADMAP ORDER
# ==========================================

ROADMAP_ORDER = [
    "Requirement Analysis",
    "System Design",
    "Database Design",
    "Backend Development",
    "Frontend Development",
    "Feature Implementation",
    "Testing",
    "Bug Fixing",
    "Documentation",
    "Final Presentation"
]


# ==========================================
# CREATE PROJECT + AUTOMATIC ROADMAP
# ==========================================

@router.post("/create")
def create_project(
    data: ProjectRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    project = Project(
        user_id=current_user,
        name=data.name,
        description=data.description,
        skills=data.skills
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    roadmap_tasks = [
        {
            "title": "Requirement Analysis",
            "description": "Understand the problem, define requirements, and identify project objectives.",
            "priority": "High"
        },
        {
            "title": "System Design",
            "description": "Design the overall system architecture and project workflow.",
            "priority": "High"
        },
        {
            "title": "Database Design",
            "description": "Design database tables, relationships, and required data fields.",
            "priority": "High"
        },
        {
            "title": "Backend Development",
            "description": "Develop backend APIs and implement the main project logic.",
            "priority": "High"
        },
        {
            "title": "Frontend Development",
            "description": "Create the user interface and connect it with the backend.",
            "priority": "Medium"
        },
        {
            "title": "Feature Implementation",
            "description": "Implement the major features required for the project.",
            "priority": "High"
        },
        {
            "title": "Testing",
            "description": "Test all project features and identify errors.",
            "priority": "Medium"
        },
        {
            "title": "Bug Fixing",
            "description": "Fix errors and improve the reliability of the application.",
            "priority": "Medium"
        },
        {
            "title": "Documentation",
            "description": "Prepare project documentation, screenshots, and technical details.",
            "priority": "Medium"
        },
        {
            "title": "Final Presentation",
            "description": "Prepare the final demonstration and presentation of the project.",
            "priority": "Low"
        }
    ]

    for item in roadmap_tasks:
        task = Task(
            project_id=project.id,
            title=item["title"],
            description=item["description"],
            priority=item["priority"],
            status="Pending"
        )

        db.add(task)

    db.commit()

    return {
        "message": "Project and roadmap created successfully",
        "project_id": project.id,
        "project_name": project.name,
        "tasks_created": len(roadmap_tasks)
    }


# ==========================================
# GET ALL PROJECTS OF CURRENT USER
# ==========================================

@router.get("/my-projects")
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    projects = db.query(Project).filter(
        Project.user_id == current_user
    ).order_by(Project.id.desc()).all()

    result = []

    for project in projects:

        tasks = db.query(Task).filter(
            Task.project_id == project.id
        ).all()

        total_tasks = len(tasks)

        completed_tasks = len([
            task
            for task in tasks
            if task.status == "Completed"
        ])

        pending_tasks = total_tasks - completed_tasks

        if total_tasks == 0:
            progress = 0
        else:
            progress = round(
                (completed_tasks / total_tasks) * 100
            )

        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "skills": project.skills,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "progress": progress
        })

    return result


# ==========================================
# ANALYZE PROJECT
# ==========================================

@router.post("/analyze/{project_id}")
def analyze_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    analysis = f"""
AI PROJECT ANALYSIS

Project Name:
{project.name}

Description:
{project.description}

Skills / Technologies:
{project.skills}

1. Project Suitability

This project is suitable for a student-level
software development project.

2. Difficulty Level

Medium

3. Required Skills

{project.skills}

Additional skills that may be useful:

- Problem solving
- Database handling
- API development
- Testing
- Documentation

4. Suggested Development Phases

Phase 1:
Requirement analysis and project planning

Phase 2:
System and database design

Phase 3:
Backend development

Phase 4:
Frontend development

Phase 5:
Feature implementation

Phase 6:
Testing and debugging

Phase 7:
Documentation and final presentation

5. Project Roadmap

The system has automatically created
development tasks for this project.

Complete each task and update its status
regularly.

6. Possible Risks

- Integration errors
- Database connection problems
- API errors
- Time management issues
- Testing delays

7. Estimated Completion Time

Approximately 2 to 4 weeks depending on
project complexity and daily work.

8. Next Recommended Step

Start with the first pending task:

Requirement Analysis
"""

    return {
        "project_id": project.id,
        "project_name": project.name,
        "analysis": analysis
    }


# ==========================================
# AI PROJECT CHATBOT
# ==========================================

@router.post("/chat")
def chat_with_project(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):

    # --------------------------------------
    # CHECK PROJECT
    # --------------------------------------

    project = db.query(Project).filter(
        Project.id == data.project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------
    # GET TASKS
    # --------------------------------------

    tasks = db.query(Task).filter(
        Task.project_id == data.project_id
    ).all()

    # Sort tasks according to roadmap order
    def task_order(task):
        if task.title in ROADMAP_ORDER:
            return ROADMAP_ORDER.index(task.title)

        return 999

    tasks.sort(key=task_order)

    # --------------------------------------
    # CALCULATE PROGRESS
    # --------------------------------------

    total_tasks = len(tasks)

    completed_tasks = len([
        task
        for task in tasks
        if task.status == "Completed"
    ])

    pending_tasks = [
        task
        for task in tasks
        if task.status != "Completed"
    ]

    pending_count = len(pending_tasks)

    if total_tasks == 0:
        progress = 0
    else:
        progress = round(
            (completed_tasks / total_tasks) * 100
        )

    message = data.message.lower().strip()

    # ======================================
    # GREETING
    # ======================================

    if message in [
        "hi",
        "hello",
        "hey",
        "hai",
        "hii",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        ai_response = (
            f"Hello! 👋\n\n"
            f"I am your AI Project Mentor for '{project.name}'.\n\n"
            f"Your current progress is {progress}%.\n\n"
            "You can ask me:\n"
            "• What should I do next?\n"
            "• What should I work on today?\n"
            "• What is my progress?\n"
            "• Show my pending tasks\n"
            "• I completed database design\n"
            "• I completed backend development\n"
            "• I am stuck in backend development\n"
            "• I have a PostgreSQL problem\n"
            "• Give me project advice"
        )

    # ======================================
    # TASK COMPLETION
    # ======================================

    elif (
        "completed" in message
        or "finished" in message
        or "done" in message
    ) and any(
        word in message
        for word in [
            "database",
            "backend",
            "frontend",
            "design",
            "testing",
            "requirement",
            "documentation",
            "presentation",
            "feature",
            "bug"
        ]
    ):

        matched_task = None

        # ----------------------------------
        # EXACT TASK MATCHING
        # ----------------------------------

        # Database Design FIRST
        if "database design" in message:

            for task in tasks:
                if task.title.lower() == "database design":
                    matched_task = task
                    break

        # System Design
        elif "system design" in message:

            for task in tasks:
                if task.title.lower() == "system design":
                    matched_task = task
                    break

        # Requirement Analysis
        elif "requirement" in message:

            for task in tasks:
                if task.title.lower() == "requirement analysis":
                    matched_task = task
                    break

        # Backend Development
        elif "backend" in message:

            for task in tasks:
                if task.title.lower() == "backend development":
                    matched_task = task
                    break

        # Frontend Development
        elif "frontend" in message:

            for task in tasks:
                if task.title.lower() == "frontend development":
                    matched_task = task
                    break

        # Feature Implementation
        elif "feature" in message:

            for task in tasks:
                if task.title.lower() == "feature implementation":
                    matched_task = task
                    break

        # Testing
        elif "testing" in message:

            for task in tasks:
                if task.title.lower() == "testing":
                    matched_task = task
                    break

        # Bug Fixing
        elif "bug" in message:

            for task in tasks:
                if task.title.lower() == "bug fixing":
                    matched_task = task
                    break

        # Documentation
        elif "documentation" in message:

            for task in tasks:
                if task.title.lower() == "documentation":
                    matched_task = task
                    break

        # Final Presentation
        elif "presentation" in message:

            for task in tasks:
                if task.title.lower() == "final presentation":
                    matched_task = task
                    break

        # ----------------------------------
        # UPDATE TASK
        # ----------------------------------

        if matched_task:

            if matched_task.status != "Completed":

                matched_task.status = "Completed"

                db.commit()
                db.refresh(matched_task)

                # Recalculate progress
                completed_tasks += 1

                pending_count = total_tasks - completed_tasks

                if total_tasks == 0:
                    progress = 0
                else:
                    progress = round(
                        (completed_tasks / total_tasks) * 100
                    )

                # ----------------------------------
                # FIND NEXT TASK IN ROADMAP ORDER
                # ----------------------------------

                next_task = None

                for roadmap_task_name in ROADMAP_ORDER:

                    for task in tasks:

                        if (
                            task.title == roadmap_task_name
                            and task.status != "Completed"
                        ):
                            next_task = task
                            break

                    if next_task:
                        break

                # ----------------------------------
                # RESPONSE
                # ----------------------------------

                ai_response = (
                    f"✅ Great work!\n\n"
                    f"I marked '{matched_task.title}' as Completed.\n\n"
                    f"Current Progress: {progress}%\n\n"
                )

                if next_task:

                    ai_response += (
                        f"📌 Your next task is:\n\n"
                        f"{next_task.title}\n\n"
                        f"{next_task.description}\n\n"
                        f"Priority: {next_task.priority}"
                    )

                else:

                    ai_response += (
                        "🎉 All project tasks are completed!\n\n"
                        "Now move to final testing, documentation "
                        "and presentation."
                    )

            else:

                ai_response = (
                    f"'{matched_task.title}' is already "
                    "marked as Completed. ✅"
                )

        else:

            ai_response = (
                "I could not identify the exact task.\n\n"
                "Please mention the task name clearly.\n\n"
                "Examples:\n"
                "• I completed requirement analysis\n"
                "• I completed system design\n"
                "• I completed database design\n"
                "• I completed backend development\n"
                "• I completed frontend development\n"
                "• I completed testing\n"
                "• I completed documentation"
            )

    # ======================================
    # NEXT TASK / TODAY'S WORK
    # ======================================

    elif (
        "today" in message
        or "next" in message
        or "what should i do" in message
        or "what do i do" in message
        or "where should i start" in message
        or "start" in message
    ):

        # Always select first pending task
        # according to roadmap order

        next_task = None

        for roadmap_task_name in ROADMAP_ORDER:

            for task in tasks:

                if (
                    task.title == roadmap_task_name
                    and task.status != "Completed"
                ):
                    next_task = task
                    break

            if next_task:
                break

        if next_task:

            ai_response = (
                f"📌 YOUR NEXT WORK\n\n"
                f"Task: {next_task.title}\n\n"
                f"Description:\n"
                f"{next_task.description}\n\n"
                f"Priority: {next_task.priority}\n\n"
                f"Project Progress: {progress}%\n\n"
                "Start this task today.\n\n"
                "After completing it, update its status to Completed."
            )

        else:

            ai_response = (
                "🎉 All roadmap tasks are completed!\n\n"
                "Your next steps are:\n"
                "• Test the complete application\n"
                "• Fix remaining errors\n"
                "• Complete documentation\n"
                "• Prepare the final presentation"
            )

    # ======================================
    # PROJECT PROGRESS
    # ======================================

    elif (
        "progress" in message
        or "how much" in message
        or "status" in message
    ):

        ai_response = (
            f"📊 PROJECT PROGRESS\n\n"
            f"Project: {project.name}\n\n"
            f"Progress: {progress}%\n\n"
            f"Total Tasks: {total_tasks}\n"
            f"Completed: {completed_tasks}\n"
            f"Pending: {pending_count}\n\n"
        )

        if progress == 0:

            ai_response += (
                "Your project has not started yet.\n\n"
                "Start with Requirement Analysis."
            )

        elif progress < 50:

            ai_response += (
                "Your project is in the early development stage.\n\n"
                "Focus on the high-priority tasks."
            )

        elif progress < 100:

            ai_response += (
                "Your project development is progressing.\n\n"
                "Continue with the remaining tasks."
            )

        else:

            ai_response += (
                "🎉 All roadmap tasks are completed!\n\n"
                "Move to final testing and documentation."
            )

    # ======================================
    # PENDING TASKS
    # ======================================

    elif (
        "pending" in message
        or "remaining" in message
        or "left" in message
    ):

        if pending_tasks:

            ai_response = "📋 PENDING TASKS\n\n"

            for task in pending_tasks:

                ai_response += (
                    f"• {task.title}\n"
                    f"  Priority: {task.priority}\n"
                    f"  Status: {task.status}\n\n"
                )

        else:

            ai_response = (
                "🎉 There are no pending tasks.\n\n"
                "All project tasks are completed!"
            )

    # ======================================
    # SHOW ALL TASKS
    # ======================================

    elif (
        "show tasks" in message
        or "list tasks" in message
        or "my tasks" in message
        or message == "tasks"
        or message == "show task"
    ):

        if not tasks:

            ai_response = (
                "There are no tasks available for this project."
            )

        else:

            ai_response = (
                f"📋 PROJECT TASKS\n\n"
                f"Total: {total_tasks}\n"
                f"Completed: {completed_tasks}\n"
                f"Pending: {pending_count}\n\n"
            )

            for task in tasks:

                ai_response += (
                    f"• {task.title}\n"
                    f"  Status: {task.status}\n"
                    f"  Priority: {task.priority}\n\n"
                )

    # ======================================
    # TROUBLESHOOTING
    # ======================================

    elif any(
        word in message
        for word in [
            "problem",
            "issue",
            "error",
            "stuck",
            "not working",
            "failed",
            "failure",
            "bug"
        ]
    ):

        # ----------------------------------
        # DATABASE / POSTGRESQL
        # ----------------------------------

        if (
            "postgresql" in message
            or "postgres" in message
            or "database" in message
            or "sql" in message
        ):

            ai_response = (
                "🔧 DATABASE / POSTGRESQL HELP\n\n"
                "Let's troubleshoot it step by step.\n\n"
                "1. Check whether PostgreSQL is running.\n"
                "2. Check the database name.\n"
                "3. Check the username and password.\n"
                "4. Check the DATABASE_URL in .env.\n"
                "5. Check whether the required table exists.\n"
                "6. Check the backend terminal for the exact error message.\n\n"
                "Send me the exact PostgreSQL error message "
                "and I can help you identify the problem."
            )

        # ----------------------------------
        # BACKEND / API
        # ----------------------------------

        elif (
            "backend" in message
            or "api" in message
            or "fastapi" in message
        ):

            ai_response = (
                "🔧 BACKEND / API HELP\n\n"
                "Check these points:\n\n"
                "1. Make sure FastAPI is running.\n"
                "2. Check the API endpoint.\n"
                "3. Check the request data.\n"
                "4. Check the JWT token.\n"
                "5. Check the backend terminal error.\n"
                "6. Test the endpoint using Swagger.\n\n"
                "Send me the exact backend error message "
                "for further help."
            )

        # ----------------------------------
        # FRONTEND / REACT
        # ----------------------------------

        elif (
            "frontend" in message
            or "react" in message
            or "vite" in message
        ):

            ai_response = (
                "🔧 FRONTEND / REACT HELP\n\n"
                "Check these points:\n\n"
                "1. Make sure React is running.\n"
                "2. Check the browser console.\n"
                "3. Check the API URL.\n"
                "4. Check whether the backend is running.\n"
                "5. Check the fetch request.\n\n"
                "Send me the exact error shown "
                "in the browser console."
            )

        # ----------------------------------
        # GENERAL PROBLEM
        # ----------------------------------

        else:

            ai_response = (
                "🛠️ PROJECT TROUBLESHOOTING\n\n"
                "Don't worry. Let's solve the problem step by step.\n\n"
                "Tell me:\n"
                "• Which task are you working on?\n"
                "• What exactly is not working?\n"
                "• What error message are you getting?\n\n"
                "I will help you identify the problem "
                "and suggest the next step."
            )

    # ======================================
    # PROJECT ADVICE
    # ======================================

    elif (
        "advice" in message
        or "suggestion" in message
        or "help" in message
        or "guide me" in message
        or "recommend" in message
    ):

        ai_response = (
            f"💡 PROJECT ADVICE\n\n"
            f"Project: {project.name}\n\n"
            f"Current Progress: {progress}%\n\n"
            "Recommended approach:\n\n"
            "1. Complete the current pending task.\n"
            "2. Focus on high-priority tasks first.\n"
            "3. Test each feature after development.\n"
            "4. Update your task status regularly.\n"
            "5. Keep your documentation updated.\n"
            "6. Solve technical issues before moving "
            "to the next major feature.\n\n"
            "Tell me what you are currently working on "
            "if you need specific guidance."
        )

    # ======================================
    # DEFAULT RESPONSE
    # ======================================

    else:

        next_task = None

        for roadmap_task_name in ROADMAP_ORDER:

            for task in tasks:

                if (
                    task.title == roadmap_task_name
                    and task.status != "Completed"
                ):
                    next_task = task
                    break

            if next_task:
                break

        ai_response = (
            f"I am monitoring your project '{project.name}'.\n\n"
            f"📊 Progress: {progress}%\n"
            f"✅ Completed: {completed_tasks}\n"
            f"⏳ Pending: {pending_count}\n\n"
        )

        if next_task:

            ai_response += (
                f"📌 Current recommended task:\n"
                f"{next_task.title}\n\n"
                f"{next_task.description}\n\n"
            )

        ai_response += (
            "You can ask me:\n"
            "• What should I do next?\n"
            "• What should I work on today?\n"
            "• What is my progress?\n"
            "• Show my pending tasks\n"
            "• I completed database design\n"
            "• I completed backend development\n"
            "• I am stuck in backend development\n"
            "• I have a PostgreSQL problem\n"
            "• Give me project advice"
        )

    # ======================================
    # SAVE CHAT HISTORY
    # ======================================

    chat = ChatHistory(
        project_id=data.project_id,
        user_message=data.message,
        ai_response=ai_response
    )

    db.add(chat)
    db.commit()

    return {
        "project_id": data.project_id,
        "user_message": data.message,
        "ai_response": ai_response
    }


# ==========================================
# CREATE MANUAL TASK
# ==========================================

@router.post("/tasks")
def create_task(
    data: TaskRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == data.project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    task = Task(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        status="Pending"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "Task created successfully",
        "task_id": task.id,
        "title": task.title,
        "status": task.status
    }


# ==========================================
# GET TASKS
# ==========================================

@router.get("/tasks/{project_id}")
def get_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).all()

    def task_order(task):

        if task.title in ROADMAP_ORDER:
            return ROADMAP_ORDER.index(task.title)

        return 999

    tasks.sort(key=task_order)

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date
        }
        for task in tasks
    ]


# ==========================================
# UPDATE TASK
# ==========================================

@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    project = db.query(Project).filter(
        Project.id == task.project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    task.status = status

    db.commit()
    db.refresh(task)

    return {
        "message": "Task updated successfully",
        "task_id": task.id,
        "title": task.title,
        "status": task.status
    }


# ==========================================
# PROGRESS ANALYSIS
# ==========================================

@router.get("/progress/{project_id}")
def analyze_progress(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).all()

    total_tasks = len(tasks)

    completed_tasks = len([
        task
        for task in tasks
        if task.status == "Completed"
    ])

    pending_tasks = total_tasks - completed_tasks

    if total_tasks == 0:
        progress = 0
    else:
        progress = round(
            (completed_tasks / total_tasks) * 100
        )

    # --------------------------------------
    # CURRENT STATUS
    # --------------------------------------

    if total_tasks == 0:

        status = "No tasks created yet."

        next_step = (
            "Create project tasks and start working "
            "on the first task."
        )

    elif progress == 100:

        status = "Project tasks are completed."

        next_step = (
            "Review the completed work, test the project, "
            "and prepare the final documentation."
        )

    elif progress >= 75:

        status = "Project is almost completed."

        next_step = (
            "Complete the remaining tasks and "
            "start final testing."
        )

    elif progress >= 50:

        status = "Project is progressing well."

        next_step = (
            "Continue working on the pending tasks "
            "and focus on high-priority tasks."
        )

    elif progress > 0:

        status = "Project development has started."

        next_step = (
            "Continue working on the pending tasks "
            "and update their status after completion."
        )

    else:

        status = "Project work has not started yet."

        next_step = (
            "Start working on the first pending task."
        )

    # --------------------------------------
    # AI ANALYSIS
    # --------------------------------------

    ai_analysis = f"""
PROJECT PROGRESS ANALYSIS

Project Name:
{project.name}

Current Progress:
{progress}%

Completed Tasks:
{completed_tasks}

Pending Tasks:
{pending_tasks}

Total Tasks:
{total_tasks}

Current Status:
{status}

What Has Been Completed:
{completed_tasks} task(s) have been completed.

What Is Still Pending:
{pending_tasks} task(s) are still pending.

Possible Risk:
If pending tasks are not completed regularly,
the project may be delayed.

What You Should Do Next:
{next_step}

Practical Suggestion:
Work on one task at a time, update the task
status after completion, and regularly check
the project progress.
"""

    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "progress": progress,
        "ai_analysis": ai_analysis
    }