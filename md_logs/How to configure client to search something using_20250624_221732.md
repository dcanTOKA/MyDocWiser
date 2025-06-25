# 📘 Final Answer Report

## 🧠 Original Question
How to configure client to search something using Tavily ?

## ✍️ Rephrased Question
How to configure a client to perform a search using Tavily?

## 📌 On Topic
✅ Yes

## 📚 Detected Library
`tavily`

## 📄 Scrape Status
✅ Done

## 📥 Ingest Status
✅ Done

## 💬 Chat History

**User:**
How to configure a client to perform a search using Tavily?


**Assistant:**
To configure a client to perform a search using Tavily, you can follow these steps in Python:

1. Install the Tavily Python SDK if you haven't already:
```bash
pip install tavily-python
```

2. Import the TavilyClient and initialize it with your API key:
```python
from tavily import TavilyClient

# Replace "tvly-YOUR_API_KEY" with your actual Tavily API key
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")
```

3. Use the `search` method on the client to perform a search query:
```python
response = tavily_client.search("Your search query here")
print(response)
```

This will perform the search and print the response.

If you don't have an API key yet, you can get a free one by signing in or creating an account on the Tavily Platform and copying your API key from the dashboard. You get 1,000 free API credits every month with no credit card required.

Let me know if you need an example in another programming language!

## 📑 Retrieved Documents
1. **API Reference**
   - *Source:* `search_9658c84eea3651d7a7b0476ffaff020d.pdf`
2. **Python**
   - *Source:* `product-news-tracker_bc66d105c9081d515754987946e69b70.pdf`
3. **Overview**
   - *Source:* `quickstart_496501c038c4e9f9a87cfe380742cdcc.pdf`
4. **Overview**
   - *Source:* `quickstart_2f8c0b13e80753fa1b92d85a6a80d491.pdf`
## 🧾 Final Answer

```python
from tavily import TavilyClient

# Replace "tvly-YOUR_API_KEY" with your actual Tavily API key
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")
```
2. Import the TavilyClient and initialize it with your API key: