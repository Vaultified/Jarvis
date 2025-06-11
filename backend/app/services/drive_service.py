from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent,
    CallToolResult,
    Tool,
    Resource,
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PyPDF2 import PdfReader
from .auth_service import get_google_credentials
import base64
import io
import re
from typing import List

mcp = FastMCP("gdrive-mcp-server", version="0.1.0")

def get_drive_service():
    creds = get_google_credentials()
    if not creds:
        raise ValueError("Authentication required for Google Drive.")
    return build("drive", "v3", credentials=creds)

def extract_text_from_pdf(binary_data: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(binary_data))
    text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    return text

@mcp.tool()
def list_resources(cursor: str = None) -> List[Resource]:
    service = get_drive_service()
    try:
        results = service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=cursor
        ).execute()

        files = results.get("files", [])
        return [
            Resource(
                uri=f"gdrive:///{file['id']}",
                mimeType=file["mimeType"],
                name=file["name"]
            ) for file in files
        ]
    except HttpError as e:
        print(f"Drive API error: {e}")
        return []

@mcp.tool()
def read_resource(uri: str) -> List[TextContent]:
    service = get_drive_service()
    file_id = uri.replace("gdrive:///", "")

    file = service.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime_type = file.get("mimeType", "application/octet-stream")
    file_name = file.get("name", "file")

    if mime_type.startswith("application/vnd.google-apps"):
        export_types = {
            "application/vnd.google-apps.document": "text/markdown",
            "application/vnd.google-apps.spreadsheet": "text/csv",
            "application/vnd.google-apps.presentation": "text/plain",
            "application/vnd.google-apps.drawing": "image/png",
        }
        export_mime = export_types.get(mime_type, "text/plain")
        res = service.files().export(fileId=file_id, mimeType=export_mime).execute()
        return [TextContent(uri=uri, mimeType=export_mime, text=res.decode("utf-8"))]

    res = service.files().get_media(fileId=file_id).execute()

    if mime_type.startswith("text/") or mime_type == "application/json":
        return [TextContent(uri=uri, mimeType=mime_type, text=res.decode("utf-8"))]
    elif mime_type == "application/pdf":
        text = extract_text_from_pdf(res)
        return [TextContent(uri=uri, mimeType="text/plain", text=text)]
    elif mime_type.startswith("image/"):
        encoded = base64.b64encode(res).decode("utf-8")
        return [TextContent(uri=uri, mimeType=mime_type, text=encoded)]
    else:
        return [TextContent(uri=uri, mimeType=mime_type, text="[Binary content not supported]")]

@mcp.tool()
def list_tools() -> List[Tool]:
    return [
        Tool(
            name="search",
            description="Search for files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        )
    ]

@mcp.tool()
def search(query: str) -> CallToolResult:
    escaped_query = re.sub(r"([\\'])", r"\\\\\\1", query)
    formatted_query = f"fullText contains '{escaped_query}'"

    service = get_drive_service()
    results = service.files().list(
        q=formatted_query,
        pageSize=10,
        fields="files(id, name, mimeType, modifiedTime, size)"
    ).execute()

    files = results.get("files", [])
    lines = [f"{f['name']} ({f['mimeType']})" for f in files]
    return CallToolResult(content=[TextContent(type="text", text=f"Found {len(files)} files:\n" + "\n".join(lines), uri=None, mimeType=None)], isError=False)

if __name__ == "__main__":
    print("Starting Google Drive MCP Python Server...")
    mcp.run()