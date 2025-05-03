import { createApp } from '@vibing-ai/sdk';
import axios from 'axios';

const app = createApp({
  name: 'Mocksy',
  description: 'AI-powered coach that helps users prepare for technical interviews with personalized guidance',
  version: '1.0.0',
});

console.log('App methods:', Object.getOwnPropertyNames(app));

const API_ENDPOINT = 'http://127.0.0.1:8000/interview';

// Local question bank for fallback responses
const questionBank = {
  reverse_string: {
    question: 'Write a function to reverse a string',
    solution: `def reverse_string(s):
    return s[::-1]

# Alternative implementation
def reverse_string_alt(s):
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return ''.join(chars)`
  },
  two_sum: {
    question: 'Given an array of integers and a target sum, return indices of the two numbers that add up to the target.',
    solution: `def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []`
  },
  fizzbuzz: {
    question: 'Write a function that prints numbers from 1 to n, but for multiples of 3 print "Fizz", for multiples of 5 print "Buzz", and for multiples of both print "FizzBuzz".',
    solution: `def fizzbuzz(n):
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
    return result`
  }
};

const plugin = {
  id: 'mocksy-coach',
  name: 'Mocksy',
  displayName: 'Mocksy',
  metadata: {
    name: 'Mocksy',
    description: 'Helps users prepare for technical interviews with personalized guidance',
  },
  initialize: async (appContext) => {
    console.log('Mocksy plugin initialized with context:', Object.keys(appContext));
    return {
      onMessage: async (message, context) => {
        const content = message?.content || '';
        console.log('Received message:', content);
        try {
          const response = await axios.post(API_ENDPOINT, {
            query: content,
            userId: context?.userId || 'anonymous',
            skillLevel: 'intermediate',
          });
          return { content: response.data.answer };
        } catch (error) {
          console.error('API request failed:', {
            message: error.message,
            code: error.code,
            response: error.response ? {
              status: error.response.status,
              data: error.response.data,
            } : null,
          });
          // Check question bank for specific matches
          for (const key in questionBank) {
            if (content.toLowerCase().includes(key) || content.toLowerCase().includes(questionBank[key].question.toLowerCase())) {
              const q = questionBank[key];
              return {
                content: `Question: ${q.question}\n\nSolution:\n\`\`\`python\n${q.solution}\n\`\`\``
              };
            }
          }
          // Handle greetings
          if (content.toLowerCase().includes('hello') || content.toLowerCase().includes('hi')) {
            return {
              content: 'Welcome to Mocksy! I can help with algorithms, system design, or mock interviews. What do you want to practice?',
            };
          }
          // Generic fallback
          return {
            content: 'Sorry, I couldn’t connect to the server. Please try again or ask about algorithms, system design, or a mock interview.',
          };
        }
      },
    };
  },
};

console.log('Attempting to register plugin with details:', JSON.stringify(plugin, null, 2));

app.registerPlugin(plugin);

console.log(`Custom log: Plugin "${plugin.name}" registered successfully`);

console.log('After registration - Registered plugins:', JSON.stringify(app.getPlugins(), null, 2));

app.initialize()
  .then(async () => {
    console.log('Mocksy app initialized successfully!');
    console.log('Final registered plugins:', JSON.stringify(app.getPlugins(), null, 2));
    // Simulate test messages
    const plugins = app.getPlugins();
    if (plugins[0]?.initialize) {
      const pluginInstance = await plugins[0].initialize({});
      const tests = [
        { content: 'hello' },
        { content: 'algorithm practice' },
        { content: 'system design question' },
        { content: 'start mock interview' },
        { content: 'prepare for google' },
        { content: 'prepare for amazon' },
        { content: 'prepare for microsoft' },
        { content: 'prepare for meta' },
        { content: 'reverse string' },
      ];
      for (const test of tests) {
        const response = await pluginInstance.onMessage(test, {});
        console.log(`Test message "${test.content}" response:`, response);
      }
    }
  })
  .catch((error) => {
    console.error('Failed to initialize app:', error);
  });