#!/usr/bin/env python3
"""
Script to download research papers from a markdown file.
Parses markdown, extracts links, and downloads files.
For LinkedIn URLs that return HTML, parses the HTML to find download links.
Skips existing files with the same size, overwrites if size differs.
"""

import os
import re
import requests
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
import time
import secrets
from bs4 import BeautifulSoup


def get_headers():
    """Return browser-like headers to avoid bot detection."""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def download_markdown(url):
    """Download the markdown file from the URL."""
    print(f"Downloading markdown from: {url}")
    response = requests.get(url, headers=get_headers(), allow_redirects=True)
    response.raise_for_status()
    return response.text


def extract_links(markdown_content):
    """Extract all links from markdown content.
    Supports both [text](url) and (url) formats.
    """
    links = []
    
    # Pattern 1: [text](url) - standard markdown links
    pattern1 = r'\[([^\]]+)\]\(([^)]+)\)'
    matches1 = re.findall(pattern1, markdown_content)
    for text, url in matches1:
        if url.startswith('http'):
            links.append(url.strip())
    
    # Pattern 2: (url) - links in parentheses (like in the table)
    pattern2 = r'\((https?://[^\)]+)\)'
    matches2 = re.findall(pattern2, markdown_content)
    for url in matches2:
        if url.startswith('http'):
            links.append(url.strip())
    
    # Pattern 3: https:// links not in parentheses or brackets (direct links)
    pattern3 = r'https?://[^\s\)\]\(]+'
    matches3 = re.findall(pattern3, markdown_content)
    for url in matches3:
        # Clean up trailing punctuation
        url = url.rstrip('.,;:')
        links.append(url.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    
    return unique_links


def get_filename_from_url(url):
    """Extract filename from URL path.
    Returns filename with extension, or None if not determinable from URL.
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    if not filename or filename == '/':
        return None
    
    # Decode URL-encoded characters
    filename = unquote(filename)
    
    return filename


def extract_download_link_from_html(html_content, base_url):
    """Extract download link from HTML using BeautifulSoup.
    Looks for element with classes 'artdeco-button artdeco-button--tertiary'.
    Returns the href URL or None.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find element with classes "artdeco-button artdeco-button--tertiary"
        # Classes can be a string, list, or None
        button = soup.find('a', class_=lambda x: x and (
            (isinstance(x, list) and 'artdeco-button' in x and 'artdeco-button--tertiary' in x) or
            (isinstance(x, str) and 'artdeco-button' in x and 'artdeco-button--tertiary' in x)
        ))
        
        if button and button.get('href'):
            download_url = button.get('href')
            # Make absolute URL if relative
            if download_url:
                download_url = urljoin(base_url, download_url)
                return download_url
        return None
    except Exception as e:
        print(f"    Warning: Error parsing HTML: {e}")
        return None


def download_file(url, output_dir):
    """Download a file from URL.
    If URL returns HTML, parses it to find download link with BeautifulSoup.
    Downloads to temp directory first with a random name, then determines filename
    from the downloaded file, and moves to output_dir after validation.
    Returns (success, filename, message)
    """
    temp_dir = None
    temp_filepath = None
    
    try:
        # Create temp directory with random prefix
        random_prefix = secrets.token_hex(8)
        temp_dir = os.path.join(tempfile.gettempdir(), f"research_papers_{random_prefix}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download file to temp location with a temporary random name
        temp_filename = f"temp_{secrets.token_hex(8)}"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        # Download file to temp location (no redirects)
        response = requests.get(url, headers=get_headers(), allow_redirects=False, stream=True, timeout=30)
        response.raise_for_status()
        
        # Download to temp file first
        with open(temp_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Check if the response is HTML
        content_type = response.headers.get('Content-Type', '').lower()
        if 'html' in content_type:
            # Read the HTML content
            with open(temp_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Extract download link from HTML
            download_url = extract_download_link_from_html(html_content, url)
            
            if download_url:
                print(f"    Found download link: {download_url}")
                # Remove the HTML file from temp
                os.remove(temp_filepath)
                # Recursively download the actual file
                return download_file(download_url, output_dir)
            else:
                # Couldn't find download link, treat as HTML file
                filename = get_filename_from_url(url)
                if not filename:
                    filename = 'document.html'
        else:
            # Not HTML, get filename from URL
            filename = get_filename_from_url(url)
            
            # If we can't determine filename from URL, use a default based on content type
            if not filename:
                if 'pdf' in content_type:
                    filename = 'document.pdf'
                else:
                    # Use hash of URL as fallback
                    url_hash = secrets.token_hex(4)
                    filename = f'document_{url_hash}'
        
        # Rename the temp file to the actual filename
        final_temp_filepath = os.path.join(temp_dir, filename)
        if temp_filepath != final_temp_filepath:
            os.rename(temp_filepath, final_temp_filepath)
            temp_filepath = final_temp_filepath
        
        # Get downloaded file size (from the actual file in temp directory)
        downloaded_size = os.path.getsize(temp_filepath)
        final_filepath = os.path.join(output_dir, filename)
        
        # Check if file exists in output directory
        if os.path.exists(final_filepath):
            existing_size = os.path.getsize(final_filepath)
            if existing_size == downloaded_size:
                # Same size, skip
                shutil.rmtree(temp_dir)
                return (True, filename, f"Skipped (same size: {existing_size} bytes)")
            else:
                # Different size, overwrite
                shutil.move(temp_filepath, final_filepath)
                shutil.rmtree(temp_dir)
                return (True, filename, f"Updated ({downloaded_size} bytes, was {existing_size} bytes)")
        else:
            # File doesn't exist, move to output directory
            shutil.move(temp_filepath, final_filepath)
            shutil.rmtree(temp_dir)
            return (True, filename, f"Downloaded ({downloaded_size} bytes)")
        
    except requests.exceptions.RequestException as e:
        # Clean up temp directory on error
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return (False, None, f"Error: {str(e)}")
    except Exception as e:
        # Clean up temp directory on error
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return (False, None, f"Unexpected error: {str(e)}")


def main():
    """Main function to orchestrate the download process."""
    markdown_url = "https://raw.githubusercontent.com/arpit20adlakha/Computer-Science-Papers-For-System-Design/master/README.md"
    output_dir = "research_papers"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_path = Path(output_dir).resolve()
    print(f"Output directory: {output_path}")
    print("-" * 80)
    
    # Download and parse markdown
    try:
        markdown_content = download_markdown(markdown_url)
        print(f"Markdown downloaded successfully ({len(markdown_content)} characters)\n")
    except Exception as e:
        print(f"Error downloading markdown: {e}")
        return
    
    # Extract links
    links = extract_links(markdown_content)
    print(f"Found {len(links)} unique links\n")
    
    # Download each file
    successful = 0
    failed = 0
    skipped = 0
    
    for i, link in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Processing: {link}")
        success, filename, message = download_file(link, output_dir)
        
        if success:
            if "Skipped" in message:
                skipped += 1
                print(f"  ✓ {message}")
            else:
                successful += 1
                print(f"  ✓ {message} -> {filename}")
        else:
            failed += 1
            print(f"  ✗ {message}")
        
        # Small delay to be polite
        time.sleep(0.5)
        print()
    
    # Summary
    print("-" * 80)
    print(f"Summary:")
    print(f"  Total links: {len(links)}")
    print(f"  Successful downloads: {successful}")
    print(f"  Skipped (same size): {skipped}")
    print(f"  Failed: {failed}")
    print(f"\nFiles saved to: {output_path}")


if __name__ == "__main__":
    main()


