# DuckDuckGo MCP Server

A simple Model Context Protocol (MCP) server that provides web search, image search, and image download capabilities using the [duckduckgo_search](https://github.com/deedy5/ddgs) library.

## Features

- **Web Search**: Search the web using DuckDuckGo with customizable region and result limits
- **Image Search**: Search for images with filters for size and type
- **Image Download**: Download images from URLs to your local machine

## Installation

### Using uv (Recommended)

1. Install [uv](https://github.com/astral-sh/uv) if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository or download the files

3. Create a virtual environment and install dependencies:
```bash
uv venv
uv pip install -r requirements.txt
```

### Using pip

1. Clone this repository or download the files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

With uv (from the project directory):
```bash
uv run python server.py
```

Or activate the virtual environment first:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python server.py
```

With standard Python:
```bash
python server.py
```

### Configuring in Claude Desktop

Add this configuration to your Claude Desktop config file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Using uv (recommended):
```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/websearch_mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

Using Python directly with virtual environment:
```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "/absolute/path/to/websearch_mcp/.venv/bin/python",
      "args": ["/absolute/path/to/websearch_mcp/server.py"]
    }
  }
}
```

## Available Tools

### web_search

Search the web using DuckDuckGo.

**Parameters:**
- `query` (required): The search query
- `max_results` (optional): Maximum number of results (default: 10)
- `region` (optional): Region code (default: "wt-wt" for worldwide)
  - Examples: "us-en", "uk-en", "de-de", "fr-fr"

**Example:**
```
Search the web for "Python MCP servers" with max 5 results
```

### image_search

Search for images using DuckDuckGo.

**Parameters:**
- `query` (required): The image search query
- `max_results` (optional): Maximum number of results (default: 10)
- `size` (optional): Image size filter
  - Options: "small", "medium", "large", "wallpaper"
- `type` (optional): Image type filter
  - Options: "photo", "clipart", "gif", "transparent", "line"

**Example:**
```
Search for "cute puppies" images, large size, photo type, max 5 results
```

### download_image

Download an image from a URL to your local machine.

**Parameters:**
- `url` (required): The URL of the image to download
- `filename` (optional): Custom filename for the downloaded image
- `download_dir` (optional): Directory to save the image (default: "./downloads")

**Example:**
```
Download image from https://example.com/image.jpg to ./my-images/
```

## Dependencies

- [duckduckgo_search](https://github.com/deedy5/ddgs) - DuckDuckGo search library
- [mcp](https://pypi.org/project/mcp/) - Model Context Protocol SDK
- [httpx](https://www.python-httpx.org/) - HTTP client for downloading images

## License

See LICENSE file for details.

## Notes

- Images are downloaded to `./downloads` by default
- The download directory will be created automatically if it doesn't exist
- Web search respects DuckDuckGo's rate limits
- All searches are anonymous (no tracking)
