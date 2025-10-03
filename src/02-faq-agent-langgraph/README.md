# FAQ Agent (LangGraph + Chroma)

In this tutorial we'll explore how to build a simple FAQ agent using LangGraph and Chroma. 

Perhaps the most important lesson here is the power of pre-transforming your data to fit your problem. 

Vector search can be unreliable but for cases where you have self contained chunks (like FAQs), it can work well. 

In this example I pre-processed the Amazon documentation into a set of self contained FAQs to better match the problem domain of question and answer. 

## Pre-Processing
Pre-processing can be a good strategy when you control the data and it doesn't change often. 

Example prompt:
```
Generate a comprehensive set of FAQs from this Amazon returns policy document.

Format each FAQ as:
# Q: [Question in natural, customer-friendly language]
A: [Clear, complete answer with relevant details]

Requirements:
- Each answer should be self-contained with enough context to understand without reading other FAQs
- Group related questions by topic (General Policy, Costs, Methods, Special Items, etc.)
- Prioritize the most common customer concerns
- Keep answers concise but complete - include details necessary to answer customer questions.
```
