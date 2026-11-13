# Program content for every internship domain.
# Each week = (theme, [5 daily tasks]); each task is "what to do | what to submit".
# Tasks are released Mon-Fri, one per working day, starting from the intern's start date.

METHOD = [
    "Enroll|Choose your internship and enroll. The UPNIVO admin team is notified instantly.",
    "Profile review|Our team reviews your profile and enrollment.",
    "Offer letter|You receive an official offer letter. Your internship unlocks only after this.",
    "Daily task|A new task is released every working day (Mon-Fri). Spend 2-3 focused hours on it.",
    "Submit and get feedback|Submit a GitHub / Drive link or notes. Mentors review and give feedback.",
    "Weekly milestone|Every week ends with a mini project that grows your portfolio.",
    "Capstone project|In the final weeks you plan, build, deploy and present a real project.",
    "Certificate|Get at least 80% of your tasks approved to earn your certificate.",
]

PROGRAMS = {
"Full Stack": {
 "roles": ["Build responsive web pages and React components", "Create REST APIs with Node.js, Express and MongoDB",
           "Use Git and GitHub every day: commit, branch, push", "Test APIs with Postman and fix bugs", "Deploy projects live and present a demo"],
 "tools": "HTML, CSS, JavaScript, React, Node.js, Express, MongoDB, Git, Postman, VS Code",
 "final": "A deployed MERN application (e-commerce, LMS, job portal or blog) with authentication, CRUD, README and a 3-minute demo video.",
 "weeks": [
  ("Web Foundations", [
   "Set up VS Code, Git and Node.js; create a GitHub repo named mern-internship | Repo link with README",
   "Build a semantic HTML profile page with your details | Screenshot + commit link",
   "Style the profile with CSS Flexbox and a custom colour palette | Updated screenshot",
   "Make the page responsive with media queries; test at mobile width | Mobile + desktop screenshots",
   "Build a landing page (hero, features, footer) using CSS Grid | Live GitHub Pages link"]),
  ("JavaScript Essentials", [
   "Practise variables, functions, arrays and objects with 10 small problems | Solutions file link",
   "Solve 10 problems using map, filter and reduce | Solutions file link",
   "Build a to-do list with pure DOM manipulation | Demo + code link",
   "Build a signup form with live validation using events | Demo + code link",
   "Fetch data from a public API and render it as cards | Demo + code link"]),
  ("Advanced JS and Tooling", [
   "Rewrite your fetch code with async/await and proper error handling | Code link",
   "Build a weather or quote app that saves favourites in localStorage | Demo link",
   "Split the app into ES modules | Code link",
   "Learn npm and package.json; migrate the project to Vite | Repo link",
   "Mini project: Movie search app with debounced search | Deployed link"]),
  ("React Basics", [
   "Create a React app with Header, Footer and Card components using props | Code link",
   "Use useState to build a counter and a dark-mode toggle | Demo link",
   "Build a to-do app with state and list rendering | Demo link",
   "Use useEffect to fetch API data with loading and error states | Demo link",
   "Build a multi-page app with React Router (Home, About, Contact) | Deployed link"]),
  ("React Advanced", [
   "Share data across components with Context API | Code link",
   "Create a custom useFetch hook and reuse it on two pages | Code link",
   "Build a controlled form with validation messages | Demo link",
   "Build a shopping cart (add, remove, quantity) with useReducer | Demo link",
   "Style with Tailwind or CSS Modules and deploy to Netlify/Vercel | Live link"]),
  ("Node.js and Express", [
   "Set up an Express server with GET /health and /hello | Code + Postman screenshot",
   "Build REST routes for a notes resource (in-memory array) | Postman collection",
   "Add middleware: logger, JSON parser and error handler | Code link",
   "Organise into routes and controllers; move config to .env | Repo link",
   "Test every endpoint in Postman and document the API in README | README link"]),
  ("MongoDB", [
   "Create a MongoDB Atlas cluster and connect it with Mongoose | Connection screenshot",
   "Design User and Task schemas with validation | Schema code link",
   "Implement full CRUD for tasks backed by MongoDB | Postman screenshots",
   "Add pagination, search and sorting to the tasks API | Code link",
   "Seed sample data and return proper status codes and error messages | Repo link"]),
  ("Authentication", [
   "Build user registration with bcrypt password hashing | Code + Postman screenshot",
   "Build login that issues a JWT | Code + Postman screenshot",
   "Write auth middleware to protect the task routes | Code link",
   "Connect React login/register pages to the API | Demo link",
   "Add protected routes and logout in React | Demo link"]),
  ("Full-Stack Integration", [
   "Connect the React Task Manager UI to the API (list + create) | Demo link",
   "Add edit, delete and mark-complete from the UI | Demo link",
   "Handle loading, empty and error states; add toast messages | Demo link",
   "Add a profile page and an update-profile API | Demo link",
   "Add CORS config, input validation (Joi/Zod) and rate limiting | Code link"]),
  ("Capstone: Plan and Build", [
   "Pick your capstone idea; write requirements and wireframes | Doc or Figma link",
   "Design the database schema and list all API endpoints | ER sketch + endpoint list",
   "Backend: models, authentication and core endpoints | Repo link",
   "Backend: remaining endpoints and validation | Postman collection",
   "Frontend: layout, routing and auth pages | Demo link"]),
  ("Capstone: Build and Polish", [
   "Frontend: main feature pages connected to the API | Demo link",
   "Frontend: forms, search, filter and pagination | Demo link",
   "Add image upload (Multer/Cloudinary) or another advanced feature | Demo link",
   "Write at least 5 API tests (Jest + Supertest) and fix bugs | Test output screenshot",
   "Polish the UI: responsive layout, accessibility, loading states | Screenshots"]),
  ("Deploy and Present", [
   "Deploy the backend to Render and the database to Atlas | Live API link",
   "Deploy the frontend to Vercel/Netlify and connect it to the live API | Live app link",
   "Write a professional README (setup, screenshots, features, stack) | README link",
   "Record a 3-minute demo video and prepare 5 slides | Video link",
   "Final presentation, self-review and a LinkedIn post about your project | Post link"]),
 ]},

"Python": {
 "roles": ["Write clean Python scripts every day", "Automate real tasks: files, email and web scraping",
           "Analyse data with Pandas and visualise it", "Build a small API with FastAPI", "Write tests and document your code"],
 "tools": "Python 3, VS Code, Git, Pandas, NumPy, Matplotlib, Requests, BeautifulSoup, FastAPI, pytest",
 "final": "A working Python project (expense tracker, quiz app, job-scraper dashboard or inventory API) with tests, README and demo video.",
 "weeks": [
  ("Python Basics", [
   "Install Python and VS Code; write Hello World and use variables and input | Script link",
   "Use operators and conditions to build a grade calculator | Script link",
   "Use loops to print number patterns and a multiplication table | Script link",
   "Write 5 reusable functions: prime, palindrome, factorial, fibonacci, vowel count | Script link",
   "Mini project: Number guessing game | Code link"]),
  ("Data Structures", [
   "Solve 10 list and tuple problems | Solutions link",
   "Build a word-frequency counter with dicts and sets | Code link",
   "Build a password strength checker using string methods | Code link",
   "Use comprehensions and sorting on a list of student records | Code link",
   "Mini project: CLI contact book (add, search, delete) | Code link"]),
  ("Files and OOP", [
   "Build an expense logger that reads and writes CSV files | Code link",
   "Add JSON storage and exception handling so it never crashes | Code link",
   "Create a BankAccount class with deposit and withdraw | Code link",
   "Build an Employee class hierarchy using inheritance | Code link",
   "Mini project: Library management with OOP and file storage | Code link"]),
  ("Libraries and Automation", [
   "Create a virtual environment, install packages and push the project to GitHub | Repo link",
   "Use requests to fetch data from a public API and display it | Code link",
   "Scrape headlines with BeautifulSoup and save them to CSV | Code + CSV link",
   "Write a file-organiser script that sorts Downloads by file type | Code link",
   "Generate an Excel report with openpyxl (or send an automated email) | Code + sample output"]),
  ("Data Analysis", [
   "Learn NumPy arrays and do 10 practice operations | Notebook link",
   "Load a CSV with Pandas and clean missing values | Notebook link",
   "Group, filter and aggregate the data | Notebook link",
   "Create 4 charts with Matplotlib/Seaborn | Notebook link",
   "Mini project: Analyse a Kaggle dataset and write 5 insights | Notebook link"]),
  ("APIs with FastAPI", [
   "Build a Hello API with FastAPI and open the /docs page | Code + screenshot",
   "Build CRUD endpoints for a to-do resource (in memory) | Code link",
   "Store the data in SQLite using SQLAlchemy | Code link",
   "Add input validation and proper error handling | Code link",
   "Add a simple HTML page that uses your API | Demo link"]),
  ("Capstone: Build", [
   "Pick your capstone idea and write a one-page plan | Plan link",
   "Create the data models and core logic | Code link",
   "Build the API or CLI features | Code link",
   "Write at least 5 tests with pytest | Test output screenshot",
   "Refactor the code and add docstrings | Repo link"]),
  ("Finish and Present", [
   "Add one advanced feature (login, charts or a scheduler) | Demo link",
   "Deploy the project (Render or PythonAnywhere) | Live link",
   "Write a README with screenshots | README link",
   "Record a 3-minute demo video | Video link",
   "Final presentation and a LinkedIn post about your project | Post link"]),
 ]},

"Java": {
 "roles": ["Solve programming problems in Java every day", "Design classes using OOP principles",
           "Work with collections, streams and JDBC", "Build REST APIs with Spring Boot", "Write unit tests and clear documentation"],
 "tools": "Java 17, IntelliJ IDEA / VS Code, Git, MySQL or PostgreSQL, JDBC, Spring Boot, Maven, JUnit, Postman",
 "final": "A Spring Boot REST API (Library, Hospital, Banking or E-commerce) with database, tests, Swagger docs and a demo video.",
 "weeks": [
  ("Java Basics", [
   "Install JDK and an IDE; understand JVM/JDK/JRE; run Hello World | Screenshot + code link",
   "Use data types, operators and Scanner to build a calculator | Code link",
   "Build an ATM menu simulation with if/else and switch | Code link",
   "Print patterns and number series with loops | Code link",
   "Mini project: Student grade calculator | Code link"]),
  ("Methods, Arrays and Strings", [
   "Write a math utility class with overloaded methods | Code link",
   "Practise 1D and 2D arrays: matrix operations | Code link",
   "Solve palindrome, anagram and word-count using String and StringBuilder | Code link",
   "Solve factorial, fibonacci and Tower of Hanoi with recursion | Code link",
   "Mini project: Console Tic-Tac-Toe | Code link"]),
  ("OOP Part 1", [
   "Create a Student class with constructors | Code link",
   "Build a BankAccount with encapsulation and validation | Code link",
   "Build a Vehicle hierarchy with inheritance and super | Code link",
   "Model Shapes with abstraction and polymorphism | Code link",
   "Mini project: Employee management using OOP | Code link"]),
  ("OOP Part 2", [
   "Build a payment system with interfaces and abstract classes | Code link",
   "Add custom exceptions to your bank app | Code link",
   "Use packages, access modifiers, static and final | Code link",
   "Use enums, wrapper classes and immutable objects | Code link",
   "Mini project: Library management with exception handling | Code link"]),
  ("Collections and Streams", [
   "Work with ArrayList and LinkedList: 10 problems | Code link",
   "Build a word counter with HashMap, HashSet and TreeMap | Code link",
   "Sort objects with Comparable and Comparator | Code link",
   "Use lambdas and Streams (filter, map, collect) on an employee list | Code link",
   "Mini project: Inventory system using collections | Code link"]),
  ("File I/O and JDBC", [
   "Read and write files; try object serialization | Code link",
   "Install MySQL/PostgreSQL; create tables and write SQL queries | SQL script link",
   "Connect with JDBC; insert and select records | Code link",
   "Update and delete with PreparedStatement; create a DAO class | Code link",
   "Mini project: Student database console app | Code link"]),
  ("Spring Boot", [
   "Set up Spring Boot and create your first REST controller | Code + Postman screenshot",
   "Build CRUD with Spring Data JPA and H2 | Code link",
   "Add DTOs, validation and a global exception handler | Code link",
   "Switch to MySQL/PostgreSQL with a layered architecture | Code link",
   "Test APIs in Postman and write unit tests with JUnit | Test screenshot"]),
  ("Capstone", [
   "Choose your capstone; draw the ER diagram and list the endpoints | Diagram + list",
   "Build entities and repositories | Code link",
   "Build services and controllers | Code link",
   "Add tests, Swagger docs and a README | Repo link",
   "Final demo video and a LinkedIn post | Video + post link"]),
 ]},

"AI/ML": {
 "roles": ["Clean and explore real datasets", "Train and evaluate ML models with scikit-learn",
           "Build neural networks for images and text", "Deploy a model as a web app or API", "Document results in notebooks and model cards"],
 "tools": "Python, Jupyter/Colab, NumPy, Pandas, scikit-learn, TensorFlow/Keras, Hugging Face, FastAPI, Streamlit/Gradio, Git",
 "final": "An end-to-end ML project (fake-news detector, resume screener, disease predictor or recommender) with a deployed demo, notebook and model card.",
 "weeks": [
  ("Python for AI", [
   "Set up Python, Colab/Jupyter and Git | Notebook + repo link",
   "Refresh Python: functions, lists and dicts (10 problems) | Notebook link",
   "Learn NumPy arrays and vectorisation | Notebook link",
   "Load and explore data with Pandas | Notebook link",
   "Mini project: Explore a CSV dataset and answer 10 questions | Notebook link"]),
  ("Data Cleaning and EDA", [
   "Handle missing values and duplicates | Notebook link",
   "Treat outliers and encode categorical columns | Notebook link",
   "Create 6 visualisations with Matplotlib/Seaborn | Notebook link",
   "Find correlations and feature insights | Notebook link",
   "Write a full EDA report on the Titanic or Housing dataset | Notebook link"]),
  ("Maths and Statistics", [
   "Calculate mean, median, variance and standard deviation | Notebook link",
   "Plot probability distributions | Notebook link",
   "Practise vectors, matrices and dot products | Notebook link",
   "Implement gradient descent from scratch | Notebook link",
   "Write a one-page summary of Week 3 in your own words | Doc link"]),
  ("Regression", [
   "Understand supervised vs unsupervised learning; do a train/test split | Notebook link",
   "Train a linear regression model with scikit-learn | Notebook link",
   "Evaluate with MSE, RMSE and R-squared | Notebook link",
   "Try polynomial regression and regularisation | Notebook link",
   "Mini project: House price prediction | Notebook link"]),
  ("Classification", [
   "Train a logistic regression classifier | Notebook link",
   "Compare kNN and decision trees | Notebook link",
   "Read a confusion matrix; compute precision, recall and F1 | Notebook link",
   "Use random forest with cross-validation | Notebook link",
   "Mini project: Customer churn or diabetes prediction | Notebook link"]),
  ("Unsupervised Learning and Features", [
   "Cluster data with K-Means | Notebook link",
   "Reduce dimensions with PCA | Notebook link",
   "Apply feature scaling and feature selection | Notebook link",
   "Tune hyperparameters with GridSearchCV | Notebook link",
   "Build an end-to-end scikit-learn Pipeline | Notebook link"]),
  ("Deep Learning Basics", [
   "Understand neural networks; build a perceptron | Notebook link",
   "Install TensorFlow/Keras; build an MLP for MNIST | Notebook link",
   "Experiment with activations, losses and optimisers | Notebook link",
   "Fight overfitting with dropout and early stopping | Notebook link",
   "Mini project: Fashion-MNIST classifier | Notebook link"]),
  ("Computer Vision", [
   "Understand and build a basic CNN | Notebook link",
   "Add data augmentation | Notebook link",
   "Use transfer learning with MobileNet or ResNet | Notebook link",
   "Train a cats-vs-dogs classifier | Notebook link",
   "Mini project: Image classifier web demo with Gradio | Demo link"]),
  ("Natural Language Processing", [
   "Preprocess text: tokenisation and stop-words | Notebook link",
   "Build Bag-of-Words and TF-IDF features | Notebook link",
   "Do sentiment analysis with classic ML | Notebook link",
   "Use a Hugging Face transformers pipeline | Notebook link",
   "Mini project: Spam detector or review sentiment app | Demo link"]),
  ("Deployment", [
   "Save and load models with joblib | Code link",
   "Serve your model through a FastAPI endpoint | Code + screenshot",
   "Build a Streamlit or Gradio interface | Demo link",
   "Containerise the app with Docker (basics) | Dockerfile link",
   "Deploy to Hugging Face Spaces or Render | Live link"]),
  ("Capstone Build", [
   "Choose your capstone and write a problem statement | Doc link",
   "Collect and clean the data | Notebook link",
   "Train a baseline model and record metrics | Notebook link",
   "Improve it; compare at least 3 models | Notebook link",
   "Build a web interface for the model | Demo link"]),
  ("Finish and Present", [
   "Do error analysis and write a model card | Doc link",
   "Deploy the capstone | Live link",
   "Clean the notebook and write the README | Repo link",
   "Record a demo video and prepare slides | Video link",
   "Final presentation and a LinkedIn post | Post link"]),
 ]},

"UI/UX": {
 "roles": ["Research users and write problem statements", "Create personas, journey maps and user flows",
           "Design wireframes and hi-fi screens in Figma", "Build a reusable design system", "Run usability tests and present a case study"],
 "tools": "Figma, FigJam, Notion, Google Forms, Maze or Useberry, Contrast checker",
 "final": "A complete UX case study (research, flows, wireframes, hi-fi design, clickable prototype and test results) published on Behance or Notion.",
 "weeks": [
  ("Foundations", [
   "Learn the UX process; set up Figma; write a one-page summary | Doc link",
   "Analyse 3 popular apps: list 5 good and 5 bad UX points for each | Doc link",
   "Learn colour, typography, spacing and grids; create a style guide | Figma link",
   "Learn frames, auto layout and components; recreate a login screen | Figma link",
   "Run a heuristic evaluation of a local business website | Report link"]),
  ("Research and Strategy", [
   "Pick a problem (food ordering, study planner...) and write a problem statement | Doc link",
   "Write interview questions and interview 3 people | Notes link",
   "Build 2 personas and an empathy map | Figma link",
   "Draw a user journey map and mark pain points | Figma link",
   "Compare 3 competitor apps and define your MVP features | Doc link"]),
  ("Design", [
   "Create the information architecture and user flow | Figma link",
   "Design low-fidelity wireframes for 6 screens | Figma link",
   "Build a mini design system: colours, buttons and inputs as components | Figma link",
   "Design hi-fi mockups for onboarding and home screens | Figma link",
   "Finish the remaining screens with a dark-mode or responsive variant | Figma link"]),
  ("Prototype and Test", [
   "Link your screens into a clickable prototype | Prototype link",
   "Run usability tests with 5 users and record notes | Notes link",
   "Analyse the findings and iterate your designs | Figma link",
   "Check accessibility (contrast, tap size) and prepare developer hand-off | Figma link",
   "Publish the case study and present it; share on LinkedIn | Case study link"]),
 ]},

"Cyber Security": {
 "roles": ["Set up and use a safe home lab", "Analyse network traffic and scan only your own lab",
           "Find and fix web vulnerabilities in practice apps", "Monitor logs and handle incidents like a SOC analyst", "Write professional security reports"],
 "tools": "VirtualBox, Kali/Ubuntu, Wireshark, Nmap, Burp Suite Community, OWASP Juice Shop/DVWA, Wazuh/ELK, OpenSSL",
 "final": "A professional security assessment report of an intentionally vulnerable lab app, with findings, severity ratings, fixes and a short presentation.",
 "weeks": [
  ("Foundations", [
   "Learn the CIA triad, threat types and attacker types; write one-page notes | Doc link",
   "Learn OSI, TCP/IP, DNS and HTTP; capture your first Wireshark trace | Screenshot + notes",
   "Set up a Linux VM and practise 30 command-line commands | Screenshot + cheat-sheet",
   "Study users, permissions and firewalls on Windows and Linux | Doc link",
   "Build a home lab with VirtualBox (2 VMs) and document it | Lab diagram + doc"]),
  ("Network Security", [
   "Compare HTTP and HTTPS traffic in Wireshark | Screenshots + notes",
   "Scan your own lab VM with Nmap (never scan others) | Scan output + notes",
   "Configure firewall rules with ufw or iptables | Rules + screenshot",
   "Learn VPNs, proxies and TLS certificates | Doc link",
   "Write a short network-security summary of your lab | Report link"]),
  ("Cryptography", [
   "Learn symmetric, asymmetric encryption and hashing | Notes link",
   "Hash files with SHA-256 and understand password hashing | Screenshot + notes",
   "Encrypt and decrypt files with OpenSSL or GPG | Screenshot + notes",
   "Study digital signatures and certificates | Doc link",
   "Write a Python file-integrity checker using SHA-256 | Code link"]),
  ("Web Application Security", [
   "Summarise the OWASP Top 10 in your own words | Doc link",
   "Install OWASP Juice Shop or DVWA locally | Screenshot",
   "Understand SQL injection in the lab app and write the fix | Notes + fix",
   "Understand XSS and CSRF in the lab app and list mitigations | Notes link",
   "Use Burp Suite on the lab app and write down your findings | Report link"]),
  ("Vulnerability Assessment", [
   "Learn vulnerability assessment, CVE and CVSS scoring | Notes link",
   "Scan your lab VM with OpenVAS or Nessus Essentials | Scan report",
   "Practise on an intentionally vulnerable lab machine and document your steps | Report link",
   "Study privilege escalation concepts and how to prevent them | Notes link",
   "Write a pentest report with executive summary and remediation | Report link"]),
  ("Defence and SOC", [
   "Learn logs and SIEM; install Wazuh or ELK in the lab | Screenshot",
   "Detect failed-login attempts from the logs | Screenshot + notes",
   "Learn malware basics and static analysis concepts (safe, no live samples) | Notes link",
   "Study the incident response lifecycle and run a paper tabletop exercise | Doc link",
   "Analyse 5 sample phishing emails (headers and links) | Report link"]),
  ("Capstone", [
   "Choose your capstone (secure a web app, SOC mini-lab or pentest report); plan it | Plan link",
   "Set up the capstone environment | Screenshot",
   "Perform the assessment | Notes link",
   "Document findings with severity ratings | Report draft",
   "Apply fixes and retest | Updated report"]),
  ("Wrap-up", [
   "Write the final report | Report link",
   "Create a security-awareness poster or slides for non-technical people | Design link",
   "Prepare answers to 20 interview questions (Security+/CEH level) | Doc link",
   "Record a short demo of your capstone | Video link",
   "Final presentation and a LinkedIn post | Post link"]),
 ]},
}

# ---------------------------------------------------------------------------
# Extra weeks and duration plans (1, 2 and 3 months = 20, 40 and 60 daily tasks)
# ---------------------------------------------------------------------------
_EXTRA = {
"Full Stack": [("Mini Project and Launch", [
   "Choose a small project idea (portfolio site, blog or to-do app) and sketch its pages | Sketch or Figma link",
   "Build the main pages using HTML, CSS and React components | Code link",
   "Add one key feature (API data, form or search) and test it on mobile | Demo link",
   "Fix bugs, improve the design and write a clear README with screenshots | README link",
   "Deploy it live (Netlify/Vercel), record a 2-minute demo and post on LinkedIn | Live link + post link"])],
"Python": [
  ("Testing and Clean Code", [
   "Learn why tests matter; write your first 5 pytest tests for an old project | Test file link",
   "Use fixtures and parametrize to test one function with many inputs | Test file link",
   "Add type hints to your code and run mypy or pyright | Code link",
   "Follow PEP 8: format with black and check with flake8 | Before/after screenshot",
   "Add logging and clear error messages to one project | Code link"]),
  ("SQL and Databases", [
   "Learn SQL basics (SELECT, WHERE, ORDER BY) on a sample database | Query file link",
   "Practise JOIN and GROUP BY with 10 queries | Query file link",
   "Design tables for a small app (students, courses) with primary and foreign keys | ER diagram",
   "Use Python's sqlite3 to insert, read, update and delete records | Code link",
   "Build a small command-line app backed by SQLite | Code link"]),
  ("Advanced Python", [
   "Write and use two decorators (a timer and a logger) | Code link",
   "Use generators to read a large file without loading it fully | Code link",
   "Learn context managers and write your own with the with statement | Code link",
   "Run tasks in parallel with threading or concurrent.futures | Code link",
   "Learn async/await and fetch 5 URLs at the same time with asyncio | Code link"]),
  ("Mini Projects Sprint", [
   "Project 1: Weather command-line app using a public API | Code link",
   "Project 2: Personal finance tracker with CSV reports and charts | Code link",
   "Project 3: Web scraper that saves daily data to SQLite | Code link",
   "Project 4: Rule-based chatbot script with at least 10 intents | Code link",
   "Put your best projects on GitHub with good READMEs | GitHub profile link"]),
  ("Mini Project and Launch", [
   "Choose a small project idea and write down 5 features | Plan link",
   "Build the core feature step by step | Code link",
   "Add one more feature and test everything | Code link",
   "Write a README with screenshots and usage steps | README link",
   "Publish on GitHub, record a 2-minute demo and post on LinkedIn | Repo + post link"])],
"Java": [
  ("Multithreading", [
   "Create threads using Thread and Runnable and print from two threads | Code link",
   "Create a race condition in a counter, then fix it with synchronized | Code link",
   "Use ExecutorService and a thread pool to run 10 tasks | Code link",
   "Use CompletableFuture to run tasks and combine results | Code link",
   "Mini project: File download simulator using threads | Code link"]),
  ("Data Structures in Java", [
   "Learn Big-O; solve Two Sum and Reverse Array | Code link",
   "Build a Stack and a Queue from scratch | Code link",
   "Build a singly linked list with add, delete and search | Code link",
   "Write bubble, selection and merge sort and compare speed | Code link",
   "Learn binary search and solve 5 easy practice problems | Solutions link"]),
  ("Testing and Build Tools", [
   "Use Git branches and make a pull request on GitHub | Pull request link",
   "Create a Maven project and add a dependency | pom.xml link",
   "Write JUnit 5 tests for your bank app | Test file link",
   "Use Mockito to mock a repository in a test | Test file link",
   "Add logging with SLF4J and clean up your code | Code link"]),
  ("Spring Boot Advanced", [
   "Add entity relationships (@OneToMany, @ManyToOne) to your API | Code link",
   "Add pagination and sorting to a list endpoint | Code link",
   "Add login with Spring Security and JWT | Code link",
   "Add role-based access for USER and ADMIN | Code link",
   "Add Swagger documentation and a Dockerfile | Repo link"]),
  ("Mini Project and Launch", [
   "Choose a small project (library, quiz or bank app) and list 5 features | Plan link",
   "Create the classes and the main flow | Code link",
   "Add file or database storage and test it | Code link",
   "Write a README with screenshots and how to run it | README link",
   "Publish on GitHub, record a 2-minute demo and post on LinkedIn | Repo + post link"])],
"AI/ML": [("Mini Project and Launch", [
   "Pick a small dataset and a clear question to answer | Dataset link + problem statement",
   "Clean and explore the data; write 5 findings | Notebook link",
   "Train two models and compare their scores | Notebook link",
   "Build a small Gradio or Streamlit demo | Demo link",
   "Write the README, record a 2-minute demo and post on LinkedIn | Repo + post link"])],
"UI/UX": [
  ("Visual Design", [
   "Colour theory: build 3 palettes and test their contrast | Figma link",
   "Typography: pick and pair fonts, build a type scale | Figma link",
   "Layout and spacing: redo a messy screen using an 8-point grid | Before/after link",
   "Icons and images: build a small icon set and use imagery well | Figma link",
   "Redesign one poorly designed screen and show before and after | Figma link"]),
  ("Mobile App Design", [
   "Read the basics of Material Design and iOS guidelines; write a summary | Doc link",
   "Design a bottom navigation, tabs and app bars | Figma link",
   "Design 5 screens for a habit or fitness app | Figma link",
   "Design a signup form with error and success states | Figma link",
   "Design empty, loading and error states for your app | Figma link"]),
  ("Interaction and Motion", [
   "Design 5 micro-interactions (button press, toggle, like) | Figma link",
   "Build an animated prototype with Smart Animate | Prototype link",
   "Design gestures and feedback (swipe, pull to refresh) | Prototype link",
   "Create an onboarding flow with animation | Prototype link",
   "Test it with 3 users and improve it | Notes + Figma link"]),
  ("Design Systems", [
   "Audit 3 screens and list the repeated elements | Doc link",
   "Create colour and text styles or variables | Figma link",
   "Build button, input and card components with variants | Figma link",
   "Build a full component library page | Figma link",
   "Write usage rules for your design system and share it | Doc link"]),
  ("UX Writing", [
   "Learn microcopy; collect 10 good and 10 bad examples from real apps | Doc link",
   "Rewrite 10 button labels and error messages | Doc link",
   "Write onboarding screen copy for an app | Figma link",
   "Write friendly empty-state and success messages | Figma link",
   "Rewrite the content of one real app screen and compare | Before/after link"]),
  ("Accessibility", [
   "Learn the WCAG basics and write a one-page summary | Doc link",
   "Check colour contrast and colour-blind views of your design | Screenshots",
   "Learn keyboard and screen-reader basics; test one website | Notes link",
   "Fix accessibility problems in one of your screens | Figma link",
   "Create an accessibility checklist for your own designs | Doc link"]),
  ("Portfolio and Career", [
   "Pick your 2 best projects and plan their case studies | Doc link",
   "Write one case study: problem, process, solution, result | Case study link",
   "Build your portfolio page on Notion, Behance or Framer | Portfolio link",
   "Update your resume and LinkedIn profile for UI/UX roles | Profile link",
   "Do a mock interview and a 1-hour design challenge | Notes link"]),
  ("Capstone Product", [
   "Choose a real problem and write a clear problem statement | Doc link",
   "Interview 5 users and summarise the findings | Notes link",
   "Create user flows and wireframes | Figma link",
   "Design the hi-fi screens and a clickable prototype | Prototype link",
   "Test with users, improve and present your final case study | Case study link"])],
"Cyber Security": [
  ("Scripting for Security", [
   "Write 5 useful Bash scripts (log search, backup, disk check) | Scripts link",
   "Write a Python port checker for your own lab VM only | Code link",
   "Write a Python script to count failed logins from a log file | Code link",
   "Write a Python password-strength and hash checker | Code link",
   "Automate a daily security report from your scripts | Code + sample output"]),
  ("Digital Forensics Basics", [
   "Learn evidence handling and chain of custody; write notes | Doc link",
   "Check file metadata and hashes of sample files | Screenshots + notes",
   "Learn disk imaging basics using a test image file | Notes link",
   "Recover deleted files from a lab image with Autopsy | Screenshots",
   "Write a short forensic report of your findings | Report link"]),
  ("Cloud Security Basics", [
   "Learn cloud models and the shared responsibility idea | Notes link",
   "Create a free-tier cloud account and enable MFA | Screenshot",
   "Learn IAM: users, roles and least privilege | Notes + screenshot",
   "Create a storage bucket and test public vs private access | Screenshots",
   "Write a cloud security checklist | Doc link"]),
  ("Secure Coding and DevSecOps", [
   "Learn secure coding rules and input validation | Notes link",
   "Fix an SQL injection bug using parameterised queries | Before/after code",
   "Store passwords safely using hashing (bcrypt) | Code link",
   "Scan code with a free tool (Semgrep or Bandit) and fix findings | Report link",
   "Add an automatic security scan in GitHub Actions | Workflow file link"]),
  ("Mini Project and Launch", [
   "Choose a small lab-only security mini project and plan it | Plan link",
   "Set up the lab and tools | Screenshot",
   "Do the assessment and note every finding | Notes link",
   "Write a short report with severity and fixes | Report link",
   "Record a 2-minute demo and post on LinkedIn | Video + post link"])],
}
_PLANS = {  # months -> indexes into that domain's weeks list (original weeks first, extra weeks after)
 "Full Stack":    {1: [0, 1, 3, 12], 2: [0, 1, 3, 5, 6, 7, 8, 12], 3: list(range(12))},
 "Python":        {1: [0, 1, 2, 12], 2: list(range(8)), 3: [0, 1, 2, 3, 4, 8, 9, 10, 5, 11, 6, 7]},
 "Java":          {1: [0, 1, 2, 12], 2: list(range(8)), 3: [0, 1, 2, 3, 4, 9, 8, 5, 6, 11, 10, 7]},
 "AI/ML":         {1: [0, 1, 3, 12], 2: [0, 1, 3, 4, 5, 6, 9, 12], 3: list(range(12))},
 "UI/UX":         {1: [0, 1, 2, 3], 2: [0, 1, 4, 2, 5, 6, 3, 10], 3: [0, 1, 4, 2, 5, 6, 7, 8, 9, 3, 10, 11]},
 "Cyber Security": {1: [0, 1, 3, 12], 2: list(range(8)), 3: [0, 1, 8, 2, 3, 4, 5, 9, 10, 11, 6, 7]},
}
# UI/UX has no showcase week; its 4 extra weeks come first so indexes 4-11 are the 8 new weeks
for _d, _w in _EXTRA.items():
    PROGRAMS[_d]["weeks"] = PROGRAMS[_d]["weeks"] + _w
    PROGRAMS[_d]["plans"] = _PLANS[_d]
for _d, _p in PROGRAMS.items():
    for _m, _idx in _p["plans"].items():
        assert all(i < len(_p["weeks"]) for i in _idx) and len(_idx) == _m * 4, (_d, _m)
PLAN_LABEL = {1: "Starter", 2: "Standard", 3: "Pro"}

# ---- 4 extra domains (programs2.py) ----
from programs2 import NEW as _NEW, NEW_PLANS as _NP
for _d, _p in _NEW.items():
    _p["plans"] = _NP[_d]; PROGRAMS[_d] = _p
