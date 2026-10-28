"""Career Campus AI - Personalized 7-Day Sprint Roadmap Generator
Dynamically creates an actionable, day-by-day learning sprint targeting the student's
weakest skills and chosen career aspirations.
"""

from __future__ import annotations

from typing import Any, Dict, List


SKILL_MODULES: Dict[str, Dict[str, Any]] = {
    "python": {
        "title": "Python Architecture & Advanced Constructs",
        "day1": {
            "focus": "Generators, Iterators & Memory Model",
            "topics": "Memory management, `yield` expressions, itertools module, list vs generator comprehensions",
            "task": "Implement a memory-efficient streaming log file reader using generators in Python.",
            "duration": "2.5 hrs",
            "deliverable": "Working Python script processing chunks of mock server logs.",
        },
        "day2": {
            "focus": "Decorators, Context Managers & Closures",
            "topics": "Higher-order functions, functools.wraps, `__enter__` and `__exit__` dunder methods",
            "task": "Write a `@timed_retry` decorator that logs execution time and retries up to 3 times on exception.",
            "duration": "2.5 hrs",
            "deliverable": "Unit-tested custom decorator suite.",
        },
        "day3": {
            "focus": "OOP & Clean Code Patterns in Python",
            "topics": "Dataclasses, `@property`, abstract base classes (abc), duck typing vs type annotations",
            "task": "Design an extensible PaymentProcessor class hierarchy using ABC and dataclasses.",
            "duration": "3.0 hrs",
            "deliverable": "Modular payment abstraction with mock Stripe/PayPal subclasses.",
        },
        "day4": {
            "focus": "Concurrency: Threading vs Asyncio vs Multiprocessing",
            "topics": "Global Interpreter Lock (GIL), asyncio event loop, aiohttp requests",
            "task": "Build an asynchronous web scraper fetching 10 endpoints concurrently with error handling.",
            "duration": "3.0 hrs",
            "deliverable": "Async script demonstrating 4x speedup over synchronous requests.",
        },
        "day5": {
            "focus": "Production Data Pipelines with Pandas & NumPy",
            "topics": "Vectorized operations, groupby optimizations, handling missing values, parquet serialization",
            "task": "Clean and aggregate a messy 50,000-row CSV dataset without using standard Python for-loops.",
            "duration": "3.5 hrs",
            "deliverable": "Jupyter notebook or Python script with benchmarked vectorized transformations.",
        },
        "day6": {
            "focus": "Automated Testing with Pytest & Mocking",
            "topics": "Fixtures, parameterized tests, monkeypatch, mocking network calls with unittest.mock",
            "task": "Achieve 95%+ branch test coverage on your Day 3 and Day 4 implementations using pytest.",
            "duration": "2.5 hrs",
            "deliverable": "Pytest report with zero warnings and high coverage.",
        },
        "day7": {
            "focus": "System Integration, Code Review & Mock Python Interview",
            "topics": "PEP 8 linting with flake8/black, profiling with cProfile, time/space trade-offs",
            "task": "Refactor your repository, run cProfile to find bottlenecks, and answer 5 live coding interview prompts.",
            "duration": "3.0 hrs",
            "deliverable": "Polished GitHub repo commit + self-graded interview scorecard.",
        },
    },
    "dsa": {
        "title": "Data Structures & Algorithmic Problem Solving",
        "day1": {
            "focus": "Big-O Asymptotics & Two-Pointer Patterns",
            "topics": "Time/space complexity analysis, fast-and-slow pointers, sliding window technique",
            "task": "Solve LeetCode #11 (Container With Most Water) and #3 (Longest Substring Without Repeating Characters).",
            "duration": "2.5 hrs",
            "deliverable": "O(N) solutions with comprehensive boundary edge cases handled.",
        },
        "day2": {
            "focus": "Stack, Monotonic Stack & Queue Masterclass",
            "topics": "LIFO vs FIFO, Monotonic stacks, evaluating Postfix expressions, circular queues",
            "task": "Implement Next Greater Element and Min-Stack supporting O(1) push, pop, and getMin.",
            "duration": "2.5 hrs",
            "deliverable": "Clean implementation of MinStack and daily temperatures problem.",
        },
        "day3": {
            "focus": "Binary Trees & BST Traversals",
            "topics": "In-order, Pre-order, Post-order, Level-order (BFS), Tree Height, Lowest Common Ancestor (LCA)",
            "task": "Implement recursive and iterative BFS/DFS for a Binary Search Tree with balance verification.",
            "duration": "3.0 hrs",
            "deliverable": "Visualized tree traversal helper with unit tests.",
        },
        "day4": {
            "focus": "Graph Algorithms: BFS, DFS & Dijkstra",
            "topics": "Adjacency lists, cycle detection in directed graphs, topological sort, shortest paths",
            "task": "Implement Course Schedule (Topological Sort / Kahn's Algorithm) and Number of Islands.",
            "duration": "3.5 hrs",
            "deliverable": "Graph class with cycle detection and connectivity algorithms.",
        },
        "day5": {
            "focus": "Dynamic Programming: 1D & 2D Memoization",
            "topics": "Top-down memoization vs bottom-up tabulation, 0/1 Knapsack, Coin Change, Longest Common Subsequence",
            "task": "Solve the Coin Change problem using both memoization and bottom-up DP table.",
            "duration": "3.5 hrs",
            "deliverable": "Comparison analysis of space optimization from O(N*M) to O(M).",
        },
        "day6": {
            "focus": "Heaps, Priority Queues & Sorting Algorithms",
            "topics": "Min-heap, Max-heap, HeapSort vs QuickSort, Top-K frequent elements",
            "task": "Build a real-time Top-K Stream Counter using a bounded Min-Heap.",
            "duration": "2.5 hrs",
            "deliverable": "Working Top-K streaming class with time complexity proofs.",
        },
        "day7": {
            "focus": "Timed Algorithmic Mock Contest & Interview Drills",
            "topics": "Speed, stress-testing, communicating solution design before coding, edge case discovery",
            "task": "Simulate a 60-minute mock interview: solve 2 medium problems under strict time limit.",
            "duration": "3.0 hrs",
            "deliverable": "Timed contest submission logs and post-test retrospective note.",
        },
    },
    "java": {
        "title": "Modern Java & Enterprise Engineering",
        "day1": {
            "focus": "JVM Internals & Memory Architecture",
            "topics": "Heap vs Stack, Garbage Collection algorithms (G1, ZGC), classloader hierarchy",
            "task": "Write a memory-profiling demonstration script triggering OutOfMemoryError and analyze heap dump.",
            "duration": "2.5 hrs",
            "deliverable": "Documented explanation of Java memory regions and GC roots.",
        },
        "day2": {
            "focus": "Java Collections Framework & Generics",
            "topics": "HashMap bucket collisions (treeify threshold), TreeMap (Red-Black), bounded wildcards `<? extends T>`",
            "task": "Implement a custom generic LRU Cache using LinkedHashMap or custom doubly linked list.",
            "duration": "3.0 hrs",
            "deliverable": "Thread-safe LRU Cache with O(1) get and put.",
        },
        "day3": {
            "focus": "Concurrency, Virtual Threads & Synchronization",
            "topics": "synchronized, volatile, ReentrantLock, ExecutorService, Java 21 Project Loom virtual threads",
            "task": "Build a producer-consumer buffer using BlockingQueue with 5 concurrent threads.",
            "duration": "3.0 hrs",
            "deliverable": "Multithreaded Java program free of race conditions and deadlocks.",
        },
        "day4": {
            "focus": "Functional Java: Streams & Lambdas",
            "topics": "Stream pipeline, parallelStreams, Collectors.groupingBy, Optional anti-patterns",
            "task": "Refactor a legacy imperative loop codebase into declarative Java Streams with custom collectors.",
            "duration": "2.5 hrs",
            "deliverable": "Clean, declarative data processing pipeline.",
        },
        "day5": {
            "focus": "Spring Boot REST API & Dependency Injection",
            "topics": "IoC container, `@Service`, `@Repository`, Spring Data JPA, Hibernate N+1 problem",
            "task": "Build a CRUD REST API for a student management system with validation and exception handling.",
            "duration": "3.5 hrs",
            "deliverable": "Running Spring Boot application with Swagger documentation.",
        },
        "day6": {
            "focus": "Unit & Integration Testing with JUnit 5 & Mockito",
            "topics": "`@Test`, `@ParameterizedTest`, Mockito `@Mock`, `@InjectMocks`, MockMvc integration testing",
            "task": "Write unit and API controller tests verifying status codes, payloads, and mock database queries.",
            "duration": "2.5 hrs",
            "deliverable": "Complete test suite running green in Maven/Gradle.",
        },
        "day7": {
            "focus": "System Design in Java & Senior Interview Prep",
            "topics": "Design patterns (Factory, Strategy, Singleton), SOLID principles, REST API idempotency",
            "task": "Architect a scalable URL shortener service on paper and answer 5 architectural interview questions.",
            "duration": "3.0 hrs",
            "deliverable": "Architectural diagrams + API design specification.",
        },
    },
    "mathematics": {
        "title": "Mathematics for Computing, AI & Analytics",
        "day1": {
            "focus": "Linear Algebra: Vectors, Matrices & Transformations",
            "topics": "Dot products, matrix multiplication, rank, determinants, vector spaces",
            "task": "Implement matrix multiplication and vector projection from scratch without NumPy.",
            "duration": "2.5 hrs",
            "deliverable": "Verified matrix arithmetic module with geometric interpretations.",
        },
        "day2": {
            "focus": "Eigendecomposition & PCA Foundations",
            "topics": "Eigenvalues, eigenvectors, covariance matrices, singular value decomposition (SVD)",
            "task": "Perform manual 2D PCA dimensionality reduction on sample student grades.",
            "duration": "3.0 hrs",
            "deliverable": "Step-by-step PCA calculation showing variance retained.",
        },
        "day3": {
            "focus": "Multivariate Calculus & Gradient Descent",
            "topics": "Partial derivatives, Jacobian, Hessian matrices, chain rule for computational graphs",
            "task": "Derive and write gradient descent to minimize Mean Squared Error for linear regression.",
            "duration": "3.0 hrs",
            "deliverable": "Mathematical derivation notebook and convergence plot.",
        },
        "day4": {
            "focus": "Probability Theory & Random Variables",
            "topics": "Conditional probability, Bayes Theorem, discrete/continuous distributions (Normal, Poisson, Binomial)",
            "task": "Build a Naive Bayes probability classifier from mathematical formulas on a toy dataset.",
            "duration": "2.5 hrs",
            "deliverable": "Probabilistic model demonstrating posterior calculation.",
        },
        "day5": {
            "focus": "Statistical Inference & Hypothesis Testing",
            "topics": "Z-score, t-tests, p-values, Central Limit Theorem, Type I and Type II errors",
            "task": "Formulate a null hypothesis and conduct an A/B test analysis on mock student assessment scores.",
            "duration": "3.0 hrs",
            "deliverable": "Statistical hypothesis testing report with confidence intervals.",
        },
        "day6": {
            "focus": "Discrete Mathematics & Graph Theory",
            "topics": "Combinatorics, pigeonhole principle, recurrence relations, modular arithmetic",
            "task": "Solve 5 classic discrete math interview problems involving Catalan numbers and graph connectivity.",
            "duration": "2.5 hrs",
            "deliverable": "Solutions manual with formal inductive proofs.",
        },
        "day7": {
            "focus": "Mathematical Modeling Capstone & Review",
            "topics": "Optimization algorithms, loss functions (Cross-Entropy, Huber), regularizations (L1/L2)",
            "task": "Summarize key mathematical formulas on a 2-page master cheat sheet and complete review quiz.",
            "duration": "2.5 hrs",
            "deliverable": "High-yield mathematical formula guide for technical interviews.",
        },
    },
    "problem_solving": {
        "title": "Algorithmic Problem Solving & System Reasoning",
        "day1": {
            "focus": "Problem Deconstruction & Invariant Analysis",
            "topics": "Loop invariants, state-space reduction, breaking ambiguous problems into sub-problems",
            "task": "Document the step-by-step thinking process for 3 logic puzzle interview questions.",
            "duration": "2.0 hrs",
            "deliverable": "Structured reasoning framework document.",
        },
        "day2": {
            "focus": "Greedy Strategies vs Dynamic Optimization",
            "topics": "Optimal substructure, greedy choice property, interval scheduling, Huffman coding",
            "task": "Solve the Activity Selection problem and prove greedy optimality vs DP.",
            "duration": "2.5 hrs",
            "deliverable": "Code implementation and mathematical contradiction proof.",
        },
        "day3": {
            "focus": "Backtracking & Exhaustive Search",
            "topics": "State-tree pruning, permutations, combinations, N-Queens problem, Sudoku solver",
            "task": "Write an efficient Sudoku solver utilizing constraint propagation and backtracking.",
            "duration": "3.0 hrs",
            "deliverable": "Backtracking algorithm solving hard 9x9 puzzles in under 100ms.",
        },
        "day4": {
            "focus": "Binary Search on Answer Range",
            "topics": "Predicate monotonic functions, finding boundary conditions, capacity allocation problems",
            "task": "Solve Koko Eating Bananas (LeetCode #875) and Capacity to Ship Packages Within D Days.",
            "duration": "2.5 hrs",
            "deliverable": "Optimized binary search algorithms with clear monotonic condition tests.",
        },
        "day5": {
            "focus": "Concurrency & Deadlock Problem Solving",
            "topics": "Resource allocation graphs, Coffman conditions, dining philosophers problem",
            "task": "Simulate and resolve the Dining Philosophers deadlock problem using resource hierarchy.",
            "duration": "3.0 hrs",
            "deliverable": "Deadlock-free concurrent simulation program.",
        },
        "day6": {
            "focus": "Real-World Debugging & Root Cause Analysis",
            "topics": "Binary search debugging (git bisect), memory leaks, thread dump inspection",
            "task": "Debug a simulated production incident where CPU spikes to 100% due to an infinite loop.",
            "duration": "2.5 hrs",
            "deliverable": "Root Cause Analysis (RCA) report and hotfix patch.",
        },
        "day7": {
            "focus": "Technical Aptitude & Problem Solving Interview",
            "topics": "Verbalizing thought processes, rapid pseudocode drafting, handling edge cases",
            "task": "Conduct a live whiteboard session solving 2 unseen novel problem prompts.",
            "duration": "2.5 hrs",
            "deliverable": "Recorded or transcribed problem-solving walkthrough notes.",
        },
    },
    "communication": {
        "title": "Engineering Communication & Technical Leadership",
        "day1": {
            "focus": "The STAR Method for Behavioral Interviews",
            "topics": "Situation, Task, Action, Result framework; quantifying achievements with metrics",
            "task": "Draft 3 detailed STAR stories covering conflict resolution, technical hurdles, and project success.",
            "duration": "2.0 hrs",
            "deliverable": "3 polished STAR interview responses ready for behavioral rounds.",
        },
        "day2": {
            "focus": "Articulating System Architecture to Non-Engineers",
            "topics": "Analogy modeling, abstracting complexity, focus on business value and user outcomes",
            "task": "Record a 3-minute explanation of how a distributed cache works tailored to a non-technical manager.",
            "duration": "2.0 hrs",
            "deliverable": "Audio or written transcript of your simplified technical pitch.",
        },
        "day3": {
            "focus": "Writing Clear Technical Design Documents (RFCs)",
            "topics": "Problem statement, non-goals, architecture diagrams, trade-off matrix, rollout plan",
            "task": "Draft a 1-page Request for Comments (RFC) proposing a new authentication feature.",
            "duration": "2.5 hrs",
            "deliverable": "Standard markdown technical design document.",
        },
        "day4": {
            "focus": "Conducting Effective & Constructive Code Reviews",
            "topics": "Empathy in review comments, nitpicks vs blocking issues, actionable suggestions",
            "task": "Review a mock pull request containing 5 subtle anti-patterns and write constructive feedback.",
            "duration": "2.0 hrs",
            "deliverable": "Inline GitHub-style code review comments.",
        },
        "day5": {
            "focus": "Blameless Post-Mortem & Incident Communication",
            "topics": "Timeline construction, five-whys root cause analysis, action items with owners",
            "task": "Write an incident post-mortem report for a mock 45-minute database outage.",
            "duration": "2.5 hrs",
            "deliverable": "Comprehensive post-mortem document with preventive action items.",
        },
        "day6": {
            "focus": "Cross-Functional Collaboration & Negotiation",
            "topics": "Managing technical debt vs product velocity, pushing back with data, stakeholder updates",
            "task": "Simulate an email negotiation resolving conflicting deadlines between Product and Engineering.",
            "duration": "2.0 hrs",
            "deliverable": "Professional stakeholder communication draft.",
        },
        "day7": {
            "focus": "Final Mock Behavioral & Culture Fit Interview",
            "topics": "Executive presence, active listening, asking insightful questions to interviewers",
            "task": "Run through 10 classic tech behavioral questions with instant self-evaluation.",
            "duration": "2.0 hrs",
            "deliverable": "Completed behavioral interview readiness checklist.",
        },
    },
}


def generate_7day_roadmap(
    weakest_skills: List[str] | None = None,
    target_role: str = "Software Engineer",
) -> Dict[str, Any]:
    """Builds a customized 7-day sprint learning roadmap.

    Args:
        weakest_skills: List of skill keys (e.g. ['dsa', 'python'])
        target_role: Name of target job role

    Returns:
        Structured 7-day roadmap with daily modules, deliverables, and estimated hours.
    """
    if not weakest_skills:
        weakest_skills = ["dsa", "python"]

    # Choose primary deficit module, and secondary if available
    primary_key = weakest_skills[0].lower() if weakest_skills else "dsa"
    if primary_key not in SKILL_MODULES:
        primary_key = "dsa"

    secondary_key = weakest_skills[1].lower() if len(weakest_skills) > 1 else "problem_solving"
    if secondary_key not in SKILL_MODULES:
        secondary_key = "problem_solving"

    primary_data = SKILL_MODULES[primary_key]
    secondary_data = SKILL_MODULES[secondary_key]

    # Structure 7-Day Sprint:
    # Days 1, 2, 4, 6 focus on primary deficit
    # Days 3, 5 integrate secondary deficit / practical build
    # Day 7 is capstone review & mock interview
    days: List[Dict[str, Any]] = [
        {
            "day": 1,
            "theme": "Diagnostic & Deep Foundations",
            "skill": primary_key.upper() if primary_key in ["dsa"] else primary_key.title(),
            "focus": primary_data["day1"]["focus"],
            "topics": primary_data["day1"]["topics"],
            "task": primary_data["day1"]["task"],
            "duration": primary_data["day1"]["duration"],
            "deliverable": primary_data["day1"]["deliverable"],
            "status": "Ready to Start",
        },
        {
            "day": 2,
            "theme": "Advanced Constructs & Patterns",
            "skill": primary_key.upper() if primary_key in ["dsa"] else primary_key.title(),
            "focus": primary_data["day2"]["focus"],
            "topics": primary_data["day2"]["topics"],
            "task": primary_data["day2"]["task"],
            "duration": primary_data["day2"]["duration"],
            "deliverable": primary_data["day2"]["deliverable"],
            "status": "Locked",
        },
        {
            "day": 3,
            "theme": "Targeted Drills (Secondary Deficit)",
            "skill": secondary_key.upper() if secondary_key in ["dsa"] else secondary_key.title(),
            "focus": secondary_data["day3"]["focus"],
            "topics": secondary_data["day3"]["topics"],
            "task": secondary_data["day3"]["task"],
            "duration": secondary_data["day3"]["duration"],
            "deliverable": secondary_data["day3"]["deliverable"],
            "status": "Locked",
        },
        {
            "day": 4,
            "theme": "Edge Cases, Debugging & Scaling",
            "skill": primary_key.upper() if primary_key in ["dsa"] else primary_key.title(),
            "focus": primary_data["day4"]["focus"],
            "topics": primary_data["day4"]["topics"],
            "task": primary_data["day4"]["task"],
            "duration": primary_data["day4"]["duration"],
            "deliverable": primary_data["day4"]["deliverable"],
            "status": "Locked",
        },
        {
            "day": 5,
            "theme": "Applied Mini-Project / Portfolio Build",
            "skill": f"{primary_key.title()} + {secondary_key.title()}",
            "focus": primary_data["day5"]["focus"],
            "topics": primary_data["day5"]["topics"],
            "task": primary_data["day5"]["task"],
            "duration": primary_data["day5"]["duration"],
            "deliverable": primary_data["day5"]["deliverable"],
            "status": "Locked",
        },
        {
            "day": 6,
            "theme": "Testing, Code Quality & Optimization",
            "skill": primary_key.upper() if primary_key in ["dsa"] else primary_key.title(),
            "focus": primary_data["day6"]["focus"],
            "topics": primary_data["day6"]["topics"],
            "task": primary_data["day6"]["task"],
            "duration": primary_data["day6"]["duration"],
            "deliverable": primary_data["day6"]["deliverable"],
            "status": "Locked",
        },
        {
            "day": 7,
            "theme": "Mock Interview, Retrospective & Capstone",
            "skill": "Placement Readiness",
            "focus": primary_data["day7"]["focus"],
            "topics": primary_data["day7"]["topics"],
            "task": primary_data["day7"]["task"],
            "duration": primary_data["day7"]["duration"],
            "deliverable": primary_data["day7"]["deliverable"],
            "status": "Locked",
        },
    ]

    total_est_hours = 19.5

    return {
        "title": f"7-Day Accelerated Upskilling Sprint: {target_role}",
        "primary_focus": primary_data["title"],
        "secondary_focus": secondary_data["title"],
        "target_role": target_role,
        "total_est_hours": total_est_hours,
        "days": days,
    }
