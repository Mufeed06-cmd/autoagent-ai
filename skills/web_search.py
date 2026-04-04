import requests

def web_search(query: str) -> str:
    # Clean the query — remove "search" prefix if user typed it
    query = query.lower().replace("search", "").strip()
    
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            },
            timeout=8
        )
        data = response.json()
        results = []

        if data.get("AbstractText"):
            results.append(f"[Answer]: {data['AbstractText']}")
            results.append(f"[Source]: {data.get('AbstractURL', '')}")

        topics = data.get("RelatedTopics", [])[:3]
        for topic in topics:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"- {topic['Text']}")

        if not results:
            return f"No direct answer found for: '{query}'. Try rephrasing."

        return "\n".join(results)

    except requests.exceptions.ConnectionError:
        return "No internet connection. Search unavailable."
    except requests.exceptions.Timeout:
        return "Search timed out."
    except Exception as e:
        return f"Search failed: {e}"