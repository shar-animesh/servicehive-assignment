Your task is to classify the user's intent based on their message.

## Intent Categories

### 1. greeting
User is just saying hello or starting a conversation.
Examples:
- "Hi"
- "Hello there"
- "Hey, how are you?"
- "Good morning"

### 2. inquiry
User is asking about the product, features, pricing, or general information.
Examples:
- "What are your pricing plans?"
- "Tell me about AutoStream"
- "How does the AI caption feature work?"
- "Do you support TikTok videos?"
- "What's the difference between Basic and Pro?"

### 3. high_intent_lead
User expresses strong interest in trying, buying, or signing up for the product.
Examples:
- "I want to try the Pro plan"
- "How do I sign up?"
- "I'd like to get started"
- "That sounds good, I want to try it"
- "I'm interested in subscribing"
- "Can I start using this for my YouTube channel?"

## Instructions
Analyze the user's message: "{{ user_message }}"

Classify it into ONE of the three categories: greeting, inquiry, or high_intent_lead.

Consider the context:
- If they're just being polite or saying hi → greeting
- If they're asking questions → inquiry  
- If they're expressing desire to use/buy/try → high_intent_lead

Return ONLY the intent category name, nothing else.
