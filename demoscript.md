# Agentic AI: Transforming Enterprise Workflows

## Introduction
<!-- Hi everyone! I'm Jesse Hughes, an AI Engineer. Today, I want to demonstrate how agentic AI is revolutionizing how we interact with enterprise systems. -->

Hi everyone! I'm Jesse Hughes, an AI Engineer, and today, I’m excited to show you how agentic AI is changing the way we interact with enterprise systems.

## Technical Overview
Traditional enterprise systems require separate integrations, custom APIs, and complex maintenance. But what if we could create an intelligent system that understands context, routes queries appropriately, and synthesizes information from multiple sources automatically? That's exactly what I've built.

## Live Demo
Let me show you how our AI assistant, Mook, handles complex enterprise queries:

### 1. Network Infrastructure Query

Let's start by asking Mook about our current network infrastructure

```text
Show me the sdwan config for big data org
```
*[Show the SD-WAN response with device status and VLANs]*

Notice how Mook automatically routes this to our SD-WAN provider and presents the information in a clear, structured format.

### 2. Change Management Query
Now let's ask about about any existing change requests that may affect our devices?

```text
Are there any change requests are currently open?
```
*[Show the Change Management response with change requests]*

Mook recognizes this as a change management query and routes it to the Change Mangement provider.


### 4. Complex Workflow Example

I'm satisfied there are no impacting changes open, I want to add a new vlan to my network infrastructure. 


```text
Raise a change request for big data org to add a new vlan. ID: 150, Name: WIFI, IP Range 192.168.1.0/24
```

It looks like Mook has composed the change request for us. 

### 5. Knowlege Base retrival exammple
Lastly, I'd like to demonstrate Mooks Knowledgebase Provider

```text
Tell me about docling
```

The system uses vector search to find relevant documentation and combines it with our network context.


## Technical Innovation
The system's power lies in its extensible architecture. Each provider—whether Change Management, SD-WAN, or the knowledge base—is implemented as a workflow provider that the AI can automatically route to. It:

Understands natural language queries

Routes requests to the appropriate provider based on context

Synthesizes information from multiple sources

Maintains conversation context

## Contact
If you would like to know more, please reach out to me!