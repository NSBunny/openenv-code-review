"""
Task bank for the CodeReview environment.
Each task has: code snippet, description, ground-truth issues, and difficulty.
"""

TASKS = [
    # ========== EASY TASKS (Syntax/obvious errors) ==========
    {
        "task_id": "easy_001",
        "difficulty": "easy",
        "description": "A function to calculate the average of a list of numbers.",
        "code_snippet": '''def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)
    return average

result = calculate_average([])
print(f"Average: {result}")
''',
        "ground_truth_issues": [
            {
                "line": "6",
                "severity": "high",
                "category": "logic",
                "description": "Division by zero when the input list is empty (len(numbers) == 0)"
            },
            {
                "line": "9",
                "severity": "medium",
                "category": "logic",
                "description": "Calling function with empty list will cause ZeroDivisionError"
            }
        ]
    },
    {
        "task_id": "easy_002",
        "difficulty": "easy",
        "description": "A function to read a file and return its contents.",
        "code_snippet": '''def read_file(filepath):
    """Read file contents and return as string."""
    f = open(filepath, 'r')
    content = f.read()
    return content

data = read_file("config.txt")
print(data)
''',
        "ground_truth_issues": [
            {
                "line": "3",
                "severity": "high",
                "category": "style",
                "description": "File handle is never closed. Should use 'with' statement or explicit f.close()"
            },
            {
                "line": "3",
                "severity": "medium",
                "category": "logic",
                "description": "No error handling for FileNotFoundError if file doesn't exist"
            }
        ]
    },

    # ========== MEDIUM TASKS (Logic bugs, edge cases) ==========
    {
        "task_id": "medium_001",
        "difficulty": "medium",
        "description": "A function implementing binary search on a sorted list.",
        "code_snippet": '''def binary_search(arr, target):
    """Find target in sorted array, return index or -1."""
    left = 0
    right = len(arr)
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

idx = binary_search([1, 3, 5, 7, 9], 5)
print(f"Found at index: {idx}")
''',
        "ground_truth_issues": [
            {
                "line": "4",
                "severity": "high",
                "category": "logic",
                "description": "right should be len(arr) - 1, not len(arr). Current code causes IndexError when mid == len(arr)"
            },
            {
                "line": "7",
                "severity": "medium",
                "category": "logic",
                "description": "Integer overflow potential with (left + right) // 2 for very large arrays. Safer: left + (right - left) // 2"
            },
            {
                "line": "1",
                "severity": "low",
                "category": "style",
                "description": "No type hints for function parameters and return value"
            }
        ]
    },
    {
        "task_id": "medium_002",
        "difficulty": "medium",
        "description": "A caching decorator for expensive function calls.",
        "code_snippet": '''def memoize(func):
    """Cache results of function calls."""
    cache = {}
    
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    return wrapper

@memoize
def fetch_user_data(user_id, include_private=False):
    """Simulate fetching user data from database."""
    import time
    time.sleep(0.1)
    return {"id": user_id, "name": f"User_{user_id}", "private": include_private}

data = fetch_user_data(1, include_private=True)
print(data)
''',
        "ground_truth_issues": [
            {
                "line": "5",
                "severity": "high",
                "category": "logic",
                "description": "wrapper only accepts *args but not **kwargs. The call with include_private=True (keyword arg) will not be cached correctly"
            },
            {
                "line": "3",
                "severity": "medium",
                "category": "logic",
                "description": "Cache grows unboundedly with no eviction policy — potential memory leak in long-running applications"
            },
            {
                "line": "7",
                "severity": "medium",
                "category": "logic",
                "description": "If args contain unhashable types (e.g., lists, dicts), 'args in cache' will raise TypeError"
            }
        ]
    },

    # ========== HARD TASKS (Architectural / Security / Subtle bugs) ==========
    {
        "task_id": "hard_001",
        "difficulty": "hard",
        "description": "A simple user authentication system with password hashing.",
        "code_snippet": '''import hashlib
import os

class AuthSystem:
    def __init__(self):
        self.users = {}
    
    def register(self, username, password):
        """Register a new user."""
        if username in self.users:
            return False
        salt = os.urandom(16).hex()
        hashed = hashlib.md5((salt + password).encode()).hexdigest()
        self.users[username] = {"salt": salt, "hash": hashed}
        return True
    
    def login(self, username, password):
        """Authenticate a user."""
        if username not in self.users:
            return False
        user = self.users[username]
        hashed = hashlib.md5((user["salt"] + password).encode()).hexdigest()
        return hashed == user["hash"]
    
    def delete_user(self, admin_user, target_user):
        """Delete a user (admin only)."""
        if target_user in self.users:
            del self.users[target_user]
            return True
        return False

auth = AuthSystem()
auth.register("alice", "password123")
print(auth.login("alice", "password123"))
''',
        "ground_truth_issues": [
            {
                "line": "13",
                "severity": "high",
                "category": "security",
                "description": "Using MD5 for password hashing is cryptographically broken. Should use bcrypt, scrypt, or argon2"
            },
            {
                "line": "23",
                "severity": "high",
                "category": "security",
                "description": "String comparison of hashes is vulnerable to timing attacks. Should use hmac.compare_digest()"
            },
            {
                "line": "26",
                "severity": "high",
                "category": "security",
                "description": "delete_user has no authorization check — any user can delete any other user. The admin_user parameter is unused"
            },
            {
                "line": "6",
                "severity": "medium",
                "category": "logic",
                "description": "Users stored in memory only — lost on restart. No persistence mechanism"
            },
            {
                "line": "33",
                "severity": "medium",
                "category": "security",
                "description": "Hardcoded weak password 'password123' in test code that might leak to production"
            }
        ]
    },
    {
        "task_id": "hard_002",
        "difficulty": "hard",
        "description": "A rate limiter for an API endpoint using sliding window.",
        "code_snippet": '''import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        """Check if client can make a request."""
        now = time.time()
        window_start = now - self.window
        
        # Remove old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]
        
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False
    
    def get_remaining(self, client_id):
        """Get remaining requests for client."""
        return self.max_requests - len(self.requests[client_id])

limiter = RateLimiter(max_requests=5, window_seconds=10)
for i in range(7):
    result = limiter.is_allowed("user_1")
    print(f"Request {i+1}: {'allowed' if result else 'blocked'}")
''',
        "ground_truth_issues": [
            {
                "line": "8",
                "severity": "high",
                "category": "logic",
                "description": "defaultdict(list) grows unboundedly — clients that stop making requests are never cleaned up (memory leak)"
            },
            {
                "line": "11",
                "severity": "medium",
                "category": "security",
                "description": "Not thread-safe — concurrent requests from same client_id can race past the limit check"
            },
            {
                "line": "16",
                "severity": "medium",
                "category": "logic",
                "description": "Cleanup iterates ALL timestamps for a client on every request — O(n) per request instead of using a more efficient data structure like deque"
            },
            {
                "line": "26",
                "severity": "low",
                "category": "logic",
                "description": "get_remaining() may return stale count since it doesn't clean old entries before counting"
            }
        ]
    }
]


def get_tasks_by_difficulty(difficulty: str):
    """Get all tasks of a specific difficulty level."""
    return [t for t in TASKS if t["difficulty"] == difficulty]


def get_task_by_id(task_id: str):
    """Get a specific task by its ID."""
    for t in TASKS:
        if t["task_id"] == task_id:
            return t
    return None


def get_all_task_ids():
    """Return all available task IDs."""
    return [t["task_id"] for t in TASKS]
