#!/usr/bin/env python3
"""
DuckDuckGo MCP Server
Provides web search, image search, and image download capabilities using duckduckgo_search
"""

import asyncio
import json
import os
from typing import Any
from pathlib import Path

import httpx
from duckduckgo_search import DDGS
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio


# Initialize the MCP server
app = Server("duckduckgo-search")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="web_search",
            description="Search the web using DuckDuckGo. Returns a list of search results with titles, URLs, and descriptions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    },
                    "region": {
                        "type": "string",
                        "description": "Region for search results (e.g., 'us-en', 'uk-en', 'de-de'). Default: 'wt-wt' (worldwide)",
                        "default": "wt-wt"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="image_search",
            description="Search for images using DuckDuckGo. Returns a list of image results with URLs, titles, and sources.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The image search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    },
                    "size": {
                        "type": "string",
                        "description": "Image size filter (small, medium, large, wallpaper)",
                        "enum": ["small", "medium", "large", "wallpaper"]
                    },
                    "type": {
                        "type": "string",
                        "description": "Image type filter (photo, clipart, gif, transparent, line)",
                        "enum": ["photo", "clipart", "gif", "transparent", "line"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="download_image",
            description="Download an image from a URL to the local machine. Returns the local file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the image to download"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename for the downloaded image. If not provided, will use the original filename from the URL."
                    },
                    "download_dir": {
                        "type": "string",
                        "description": "Directory to save the image (default: ./downloads)",
                        "default": "./downloads"
                    }
                },
                "required": ["url"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "web_search":
        query = arguments.get("query")
        max_results = arguments.get("max_results", 10)
        region = arguments.get("region", "wt-wt")

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    region=region,
                    max_results=max_results
                ))

            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. **{result.get('title', 'No title')}**\n"
                    f"   URL: {result.get('href', 'N/A')}\n"
                    f"   {result.get('body', 'No description')}\n"
                )

            response = f"Found {len(results)} results for '{query}':\n\n" + "\n".join(formatted_results)

            return [TextContent(
                type="text",
                text=response
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error performing web search: {str(e)}"
            )]

    elif name == "image_search":
        query = arguments.get("query")
        max_results = arguments.get("max_results", 10)
        size = arguments.get("size")
        image_type = arguments.get("type")

        try:
            with DDGS() as ddgs:
                kwargs = {
                    "keywords": query,
                    "max_results": max_results
                }
                if size:
                    kwargs["size"] = size
                if image_type:
                    kwargs["type_image"] = image_type

                results = list(ddgs.images(**kwargs))

            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. **{result.get('title', 'No title')}**\n"
                    f"   Image URL: {result.get('image', 'N/A')}\n"
                    f"   Thumbnail: {result.get('thumbnail', 'N/A')}\n"
                    f"   Source: {result.get('source', 'N/A')}\n"
                    f"   Width: {result.get('width', 'N/A')}px, Height: {result.get('height', 'N/A')}px\n"
                )

            response = f"Found {len(results)} images for '{query}':\n\n" + "\n".join(formatted_results)

            return [TextContent(
                type="text",
                text=response
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error performing image search: {str(e)}"
            )]

    elif name == "download_image":
        url = arguments.get("url")
        filename = arguments.get("filename")
        download_dir = arguments.get("download_dir", "./downloads")

        try:
            # Create download directory if it doesn't exist
            Path(download_dir).mkdir(parents=True, exist_ok=True)

            # Determine filename
            if not filename:
                filename = url.split("/")[-1].split("?")[0]
                if not filename or "." not in filename:
                    filename = "image.jpg"

            filepath = os.path.join(download_dir, filename)

            # Download the image
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True, timeout=30.0)
                response.raise_for_status()

                # Write to file
                with open(filepath, "wb") as f:
                    f.write(response.content)

            file_size = os.path.getsize(filepath)

            return [TextContent(
                type="text",
                text=f"Successfully downloaded image to: {filepath}\nFile size: {file_size:,} bytes"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error downloading image: {str(e)}"
            )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
