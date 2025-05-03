from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from pathlib import Path
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Mocksy - Technical Interview Coach API")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create base directory path
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Try to load Hugging Face model with PyTorch, with fallback
nlp = None
try:
    logger.info("Loading question-answering model with PyTorch...")
    from transformers import pipeline
    nlp = pipeline('question-answering', model='distilbert-base-cased-distilled-squad', framework='pt')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    logger.info("Continuing without NLP model - will use predefined responses")
    nlp = None

# Context data for interview topics with Mocksy's engaging tone
interview_contexts = {
    "algorithms": """
    Let's tackle algorithms! These are key for technical interviews. You'll want to master sorting (quicksort, mergesort),
    searching (binary search, DFS, BFS), and graph algorithms (Dijkstra's, A*). Time and space complexity analysis are crucial 
    - be ready to discuss Big O notation for everything you implement. I can help you practice these step by step!
    """,
    "data_structures": """
    Data structures are the building blocks of efficient code! For interviews, you'll need to master arrays, linked lists, 
    stacks, queues, hash tables, trees (binary trees, BSTs, AVL trees), heaps, and graphs. Know their operations, time 
    complexities, and when to use each one. I'd recommend implementing them from scratch for practice, and I can help you 
    work through any challenges you encounter!
    """,
    "system_design": """
    System design interviews test how you approach complex architectural challenges. We'll focus on distributed systems, 
    microservices, database design, caching strategies, load balancing, and scaling solutions. The key is understanding 
    trade-offs between different approaches and clearly explaining your reasoning. Let's work through some common scenarios 
    together!
    """,
    "general": """
    I'm Mocksy, your Technical Interview Coach! I can help you prepare for algorithms, data structures, system design questions,
    and company-specific formats. We'll work on problem-solving skills, technical knowledge, and communication abilities 
    together. Let's create a solid preparation plan with practice problems, CS fundamentals review, and mock interviews 
    tailored to your target companies!
    """
}

# Company-specific interview guidance with sample questions
company_info = {
    "google": """
    For Google interviews, let's focus on algorithms and scalability! Google's interview process typically includes:
    - Multiple algorithm and data structure questions
    - System design for senior roles
    - Strong emphasis on code quality and efficiency
    - Behavioral questions based on leadership and teamwork
    Google interviewers look for optimal solutions and the ability to analyze time and space complexity. I recommend practicing 
    problems that involve graph algorithms, dynamic programming, and searching/sorting techniques. Remember to talk through your 
    thought process clearly!

    **Sample Questions**:
    **Reverse a Linked List**: Write a function to reverse a singly linked list.
    ```python
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next

    def reverseList(head):
        prev = None
        current = head
        while current:
            next_temp = current.next
            current.next = prev
            prev = current
            current = next_temp
        return prev
    ```

    **Find Median in Two Sorted Arrays**: Given two sorted arrays, find their median.
    ```python
    def findMedianSortedArrays(nums1, nums2):
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1
        x, y = len(nums1), len(nums2)
        start, end = 0, x
        while start <= end:
            partitionX = (start + end) // 2
            partitionY = (x + y + 1) // 2 - partitionX
            maxLeftX = float('-inf') if partitionX == 0 else nums1[partitionX - 1]
            minRightX = float('inf') if partitionX == x else nums1[partitionX]
            maxLeftY = float('-inf') if partitionY == 0 else nums2[partitionY - 1]
            minRightY = float('inf') if partitionY == y else nums2[partitionY]
            if maxLeftX <= minRightY and maxLeftY <= minRightX:
                if (x + y) % 2 == 0:
                    return (max(maxLeftX, maxLeftY) + min(minRightX, minRightY)) / 2
                return max(maxLeftX, maxLeftY)
            elif maxLeftX > minRightY:
                end = partitionX - 1
            else:
                start = partitionX + 1
    ```

    **Valid Palindrome**: Check if a string is a palindrome, ignoring non-alphanumeric characters.
    ```python
    def isPalindrome(s):
        s = ''.join(c.lower() for c in s if c.isalnum())
        return s == s[::-1]
    ```
    """,
    "amazon": """
    For Amazon interviews, I recommend emphasizing their Leadership Principles. Prepare for:
    - Algorithm and data structure questions
    - System design questions focusing on scalability and reliability
    - Behavioral questions using the STAR method
    - Questions about Amazon's Leadership Principles
    Focus on customer-obsessed designs and efficient algorithms. Amazon particularly values ownership, diving deep into 
    problems, and delivering results.

    **Sample Questions**:
    **Two Sum**: Given an array of integers and a target sum, return indices of two numbers that add up to the target.
    ```python
    def two_sum(nums, target):
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
    ```

    **LRU Cache**: Design a Least Recently Used (LRU) cache with O(1) get and put operations.
    ```python
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity):
            self.cache = OrderedDict()
            self.capacity = capacity
        
        def get(self, key):
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]
        
        def put(self, key, value):
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    ```

    **Maximum Subarray**: Find the contiguous subarray with the largest sum.
    ```python
    def maxSubArray(nums):
        max_sum = current_sum = nums[0]
        for num in nums[1:]:
            current_sum = max(num, current_sum + num)
            max_sum = max(max_sum, current_sum)
        return max_sum
    ```
    """,
    "microsoft": """
    For Microsoft interviews, I'll help you focus on problem-solving and practical coding. Expect:
    - Algorithm questions with emphasis on implementation details
    - Object-oriented design problems
    - Behavioral questions about teamwork and project experience
    - System design questions for senior roles
    Microsoft values clean, maintainable code and practical problem-solving approaches.

    **Sample Questions**:
    **Merge Two Sorted Lists**: Merge two sorted linked lists into one sorted list.
    ```python
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next
        
    def mergeTwoLists(l1, l2):
        dummy = ListNode(0)
        current = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                current.next = l1
                l1 = l1.next
            else:
                current.next = l2
                l2 = l2.next
            current = current.next
        current.next = l1 if l1 else l2
        return dummy.next
    ```

    **Valid Parentheses**: Check if a string of parentheses is valid.
    ```python
    def isValid(s):
        stack = []
        brackets = {')': '(', '}': '{', ']': '['}
        for char in s:
            if char in brackets.values():
                stack.append(char)
            elif char in brackets:
                if not stack or stack.pop() != brackets[char]:
                    return False
        return len(stack) == 0
    ```

    **Spiral Matrix**: Return all elements of an m x n matrix in spiral order.
    ```python
    def spiralOrder(matrix):
        if not matrix:
            return []
        result = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        while top <= bottom and left <= right:
            for j in range(left, right + 1):
                result.append(matrix[top][j])
            top += 1
            for i in range(top, bottom + 1):
                result.append(matrix[i][right])
            right -= 1
            if top <= bottom:
                for j in range(right, left - 1, -1):
                    result.append(matrix[bottom][j])
                bottom -= 1
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    result.append(matrix[i][left])
                left += 1
        return result
    ```
    """,
    "meta": """
    For Meta (Facebook) interviews, I recommend focusing on coding efficiency and product sense. Their process typically includes:
    - Algorithm questions with emphasis on optimization
    - System design with focus on scale and user experience
    - Behavioral questions about impact and collaboration
    - Product design questions for some roles
    Meta values fast execution and impact. Their coding questions often involve arrays, strings, and graphs.

    **Sample Questions**:
    **Longest Substring Without Repeating Characters**: Find the length of the longest substring without repeating characters.
    ```python
    def lengthOfLongestSubstring(s):
        seen = {}
        max_length = start = 0
        for end, char in enumerate(s):
            if char in seen and seen[char] >= start:
                start = seen[char] + 1
            else:
                max_length = max(max_length, end - start + 1)
            seen[char] = end
        return max_length
    ```

    **Top K Frequent Elements**: Given an array, return the k most frequent elements.
    ```python
    from collections import Counter

    def topKFrequent(nums, k):
        count = Counter(nums)
        return [num for num, _ in count.most_common(k)]
    ```

    **Group Anagrams**: Group a list of strings into anagrams.
    ```python
    from collections import defaultdict

    def groupAnagrams(strs):
        anagrams = defaultdict(list)
        for s in strs:
            key = ''.join(sorted(s))
            anagrams[key].append(s)
        return list(anagrams.values())
    ```
    """
}

# Common programming questions with Mocksy-style explanations
programming_questions = {
    "reverse_string": {
        "question": "Write a function to reverse a string",
        "difficulty": "Easy",
        "solution": """
def reverse_string(s):
    return s[::-1]

# Alternative implementation
def reverse_string_alt(s):
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return ''.join(chars)
        """,
        "explanation": """
Great question! There are two common approaches to reversing a string:
- **Using Python's slice notation** - This is clean and Pythonic: `s[::-1]` creates a new string by stepping backwards through the original
- **Two-pointer technique** - This is more universal across languages:
  - Convert string to array of characters
  - Initialize pointers at the beginning and end
  - Swap characters and move pointers inward
  - Join characters back into string
The slice approach is O(n) time and space. The two-pointer approach is also O(n), but better demonstrates your understanding of fundamental algorithms. Let me know if you'd like to practice this with different constraints!
"""
    },
    "two_sum": {
        "question": "Given an array of integers and a target sum, return indices of the two numbers that add up to the target.",
        "difficulty": "Easy",
        "solution": """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
        """,
        "explanation": """
The Two Sum problem is a classic! Let's break down the optimal approach:
- We use a hash map (dictionary) to store numbers we've seen and their indices
- For each number, we calculate its "complement" (target - current number)
- If the complement exists in our hash map, we've found our pair
- Otherwise, we add the current number and its index to the hash map
This gives us O(n) time complexity with a single pass through the array, which is much better than the O(n²) brute force approach of checking every pair. This pattern of using a hash map to achieve O(1) lookups is extremely common in interview problems. It's definitely a technique worth mastering! Would you like to try a variation like Three Sum or Two Sum II?
"""
    },
    "fizzbuzz": {
        "question": "Write a function that prints numbers from 1 to n, but for multiples of 3 print 'Fizz', for multiples of 5 print 'Buzz', and for multiples of both print 'FizzBuzz'.",
        "difficulty": "Easy",
        "solution": """
def fizzbuzz(n):
    result = []
    for i in range(1, n+1):
        if i % 3 == 0 and i % 5 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
        """,
        "explanation": """
FizzBuzz is a classic programming problem that tests your understanding of conditional logic! The key insights:
- Check for multiples of both 3 and 5 first (the "and" condition)
- Then check for multiples of 3 or 5 individually
- Otherwise, just convert the number to a string
A common mistake is checking the individual conditions first - this would incorrectly return "Fizz" or "Buzz" for numbers that should be "FizzBuzz". This problem seems simple but actually reveals your attention to detail and ability to translate requirements to code. Many companies use variations of FizzBuzz as a basic screening question. Fun extension: Can you solve this without using modulo (%) operations?
"""
    }
}

# Mocksy's encouraging feedback templates
feedback_templates = [
    "Nice work! {positive}. One thing to consider: {improvement}. {next_step}",
    "You're on the right track! {positive}. To optimize further: {improvement}. {next_step}",
    "Good solution! {positive}. For interviews, also think about: {improvement}. {next_step}",
    "That's a solid approach! {positive}. A small suggestion: {improvement}. {next_step}"
]

# Mocksy's positive feedback components
positive_feedback = [
    "Your solution correctly handles the core logic",
    "You've chosen an efficient data structure for this problem",
    "Your time complexity analysis is spot on",
    "You've broken down the problem very well",
    "Your code is clean and readable",
    "You caught the edge cases"
]

# Mocksy's improvement suggestions
improvement_suggestions = [
    "consider adding comments to explain your approach",
    "think about how to optimize the space complexity",
    "make sure to validate inputs at the beginning",
    "try to use more descriptive variable names",
    "explore if there's a more efficient algorithm for this",
    "think about how to handle potential overflow issues"
]

# Mocksy's next step suggestions
next_steps = [
    "Ready to try a similar but slightly harder problem?",
    "Would you like to analyze the time and space complexity together?",
    "Can you think of any edge cases we should test?",
    "Let me know if you'd like to see an alternative approach!",
    "Want to practice explaining this solution as you would in an interview?",
    "Should we move on to another common interview topic?"
]

# Request model
class InterviewQuery(BaseModel):
    query: str
    userId: str = 'anonymous'
    skillLevel: str = 'intermediate'

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface from templates folder"""
    try:
        html_path = BASE_DIR / "templates" / "index.html"
        logger.info(f"Attempting to serve index.html from: {html_path}")
        if not html_path.exists():
            logger.error(f"index.html not found at: {html_path}")
            raise HTTPException(status_code=404, detail=f"index.html not found at {html_path}")
        with open(html_path, "r", encoding='utf-8') as f:
            content = f.read()
            logger.info("Successfully read index.html")
            return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Failed to serve index.html: {str(e)}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Mocksy - Technical Interview Coach</title>
            </head>
            <body>
                <h1>Mocksy</h1>
                <p>Error: Unable to load Mocksy interface. Please check server logs.</p>
            </body>
            </html>
            """,
            status_code=500
        )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon"""
    favicon_path = BASE_DIR / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    raise HTTPException(status_code=404, detail="Favicon not found")

@app.post("/interview")
async def interview(data: InterviewQuery):
    """Process interview queries with Mocksy's personality"""
    query = data.query.lower()
    skill_level = data.skillLevel.lower()
    logger.info(f"Received query: {query}, skillLevel: {skill_level}")

    # Adjust response based on skill level
    context_modifier = " Focus on basic concepts and clear explanations." if skill_level == 'beginner' else ""

    # Programming questions with detailed Mocksy-style responses
    for key, question_data in programming_questions.items():
        key_words = key.split('_')
        if (key in query or 
            question_data["question"].lower() in query or 
            any(word in query for word in key_words)):
            logger.info(f"Matched programming question: {key}")
            difficulty = f"**{question_data['difficulty']}**" if "difficulty" in question_data else ""
            explanation = question_data.get("explanation", "")
            feedback = feedback_templates[0].format(
                positive=positive_feedback[0],
                improvement=improvement_suggestions[0],
                next_step=next_steps[0]
            )
            return {
                "answer": f"Here's a common interview question: **{question_data['question']}** {difficulty}\n\n"
                        f"Solution:\n```python\n{question_data['solution']}\n```\n\n{explanation}\n\n**Mocksy's Feedback**: {feedback}"
            }

    # Company-specific with Mocksy's engaging tone
    for company, info in company_info.items():
        if f"help me prepare for {company}" in query or f"prepare for {company}" in query or f"{company} interview" in query:
            logger.info(f"Using {company}-specific response")
            return {"answer": info}

    # Mocksy's customized topic responses
    if "data structures" in query or "practice data structures" in query:
        return {"answer": f"""
        Let's dive into data structures! These are essential building blocks for solving technical interview problems efficiently.
        Here's what you should master:
        - Arrays & Linked Lists: Sequential storage vs. linked elements
        - Stacks & Queues: LIFO and FIFO data structures
        - Hash Tables: O(1) lookups with proper hash functions
        - Trees: Binary, BST, AVL, Red-Black trees
        - Graphs: Adjacency lists/matrices, traversal algorithms
        - Heaps: Priority queues implementation
        **Sample Problem**: Implement a stack using two queues.
        ```python
        from collections import deque

        class Stack:
            def __init__(self):
                self.q1 = deque()
                self.q2 = deque()
            
            def push(self, x):
                self.q2.append(x)
                while self.q1:
                    self.q2.append(self.q1.popleft())
                self.q1, self.q2 = self.q2, self.q1
            
            def pop(self):
                if self.q1:
                    return self.q1.popleft()
                return None
            
            def top(self):
                if self.q1:
                    return self.q1[0]
                return None
            
            def empty(self):
                return len(self.q1) == 0
        ```
        The trick here is making one queue behave like a stack by reorganizing elements with each push. {context_modifier}
        Would you like to discuss the time complexity of these operations?
        """}

    if any(word in query for word in ["algorithm", "algorithms", "algo", "practice algorithms"]):
        return {"answer": f"""
        Let's sharpen your algorithm skills! Here are the key areas to focus on:
        - **Sorting**: QuickSort, MergeSort, HeapSort (understand divide & conquer)
        - **Searching**: Binary Search, DFS, BFS (graph/tree traversal fundamentals)
        - **Dynamic Programming**: Breaking problems into overlapping subproblems
        - **Greedy Algorithms**: Making locally optimal choices
        - **Backtracking**: Exploring all potential solutions
        Always analyze time and space complexity using Big O notation, and be ready to explain trade-offs between different approaches.
        **Sample Problem**: Find the first bad version in a sequence.
        ```python
        def firstBadVersion(n):
            left, right = 1, n
            while left < right:
                mid = left + (right - left) // 2
                if isBadVersion(mid):
                    right = mid
                else:
                    left = mid + 1
            return left
        ```
        This is a classic binary search problem. Notice how we avoid integer overflow with `left + (right - left) // 2`. {context_modifier}
        Would you like to try a similar problem or explore another algorithm topic?
        """}

    if any(word in query for word in ["system design", "design system"]):
        return {"answer": f"""
        System design interviews assess your ability to architect scalable, reliable, and efficient systems. Let's break down the key components:
        - **Requirements Clarification**
          - Functional requirements: What should the system do?
          - Non-functional requirements: Scale, latency, consistency, availability
        - **High-Level Design**
          - Key components and their relationships
          - API design
          - Data model
        - **Detailed Design**
          - Database choice (SQL vs NoSQL)
          - Caching strategy
          - Load balancing
          - Sharding approach
        - **Scaling & Bottlenecks**
          - Identify potential bottlenecks
          - Propose solutions for horizontal/vertical scaling
        **Sample Problem**: Design a URL shortening service like Bitly.
        - **Core Components**:
          - Hash function to generate short URLs
          - Database to store URL mappings
          - API endpoints (create short URL, redirect)
        - **Scaling Considerations**:
          - Read-heavy workload (many redirects, fewer creations)
          - Caching frequently accessed URLs
          - Database sharding by URL hash
        {context_modifier}
        Would you like me to expand on any part of this system design example?
        """}

    if any(word in query for word in ["mock interview", "mock", "interview me"]):
        return {"answer": f"""
        Let's start a mock interview! I'll pose a common interview question, and you can share your solution.
        **Problem: Valid Parentheses**
        Given a string containing just the characters '(', ')', '{{', '}}', '[' and ']', determine if the input string is valid.
        An input string is valid if:
        - Open brackets must be closed by the same type of brackets.
        - Open brackets must be closed in the correct order.
        **Examples**:
        - "()" → true
        - "()[]{{}}" → true
        - "(]" → false
        - "([)]" → false
        - "{{[]}}" → true
        Take your time to think through this problem. When you're ready, share your approach and code implementation. I'll provide 
        feedback just like a real interviewer would! Remember to:
        - Talk through your thought process
        - Consider edge cases
        - Analyze the time and space complexity
        {context_modifier}
        Whenever you're ready, I'll be here to review your solution!
        """}

    if any(word in query for word in ["prepare", "preparation", "study plan", "how to prepare"]):
        return {"answer": f"""
        # Mocksy's Technical Interview Preparation Guide
        Here's a structured plan to maximize your interview success:
        ## 1. Fundamentals First (2-3 weeks)
        - **Data Structures**: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables
        - **Algorithms**: Sorting, Searching, Recursion, Dynamic Programming, Greedy Algorithms
        - **Time & Space Complexity**: Learn to analyze and optimize your solutions
        ## 2. Deliberate Practice (3-4 weeks)
        - Solve 2-3 problems daily on platforms like LeetCode or HackerRank
        - Start with easy problems, gradually increase difficulty
        - Categorize problems by topic to identify patterns
        - Revisit problems you struggled with after a week
        ## 3. Mock Interviews (2 weeks)
        - Practice with friends or online platforms like Pramp
        - Time yourself (typically 45 minutes per problem)
        - Explain your thought process out loud
        - Get feedback on both technical and communication skills
        ## 4. Company-Specific Prep (1-2 weeks)
        - Research common interview questions for your target companies
        - Study their tech stack and recent projects
        - Prepare for behavioral questions using the STAR method
        - Develop thoughtful questions to ask your interviewers
        ## Key Success Factors:
        - Consistency beats cramming
        - Understanding beats memorization
        - Communication is as important as correctness
        - Stress management through preparation
        {context_modifier}
        Would you like to focus on any specific part of this preparation plan?
        """}

    # Greetings and introduction
    if any(word in query for word in ["hello", "hi", "hey", "greetings"]):
        return {"answer": f"""
        Hi there! I'm Mocksy, your AI Technical Interview Coach. I'm here to help you prepare for coding interviews at top tech 
        companies. Here's how I can help you:
        - Practice algorithm and data structure problems
        - Learn system design principles
        - Prepare for specific companies like Google, Amazon, Microsoft, and Meta
        - Create a personalized study plan
        - Provide detailed feedback on your solutions
        {context_modifier}
        What would you like to focus on today? Feel free to try any of the topic buttons above, or ask me about a specific 
        concept you'd like to practice!
        """}

    # General response with Mocksy's personality
    context = interview_contexts["general"] + context_modifier
    for topic, topic_context in interview_contexts.items():
        if topic in query:
            context = topic_context + context_modifier
            logger.info(f"Using {topic} context")
            break

    if nlp:
        try:
            logger.info("Querying Hugging Face model")
            result = nlp(question=query, context=context)
            answer = result['answer']
            if len(answer) < 50:
                answer = f"{answer}\n\nTo elaborate further: {context.strip()[:300]}..."
            answer = f"{answer}\n\n**Mocksy's Tip**: Keep practicing similar questions to build confidence! {next_steps[0]}"
            return {"answer": answer}
        except Exception as e:
            logger.error(f"Model inference error: {e}")

    return {
        "answer": f"I'm Mocksy, your Technical Interview Coach! I can help you prepare for algorithms, data structures, system "
                f"design questions, and company-specific interviews.\n\n{context[:300]}...\n\nIs there a specific topic or "
                f"company you're preparing for? Try asking about 'Google interview tips' or 'Two Sum problem'!"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Mocksy Technical Interview Coach API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)