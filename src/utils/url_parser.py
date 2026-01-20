"""
PRISMA - URL Parser
===================
Utilities for extracting, validating, and processing URLs
from text content and files.
"""

import re
from typing import List, Set, Tuple
from urllib.parse import urlparse, urljoin
from pathlib import Path

from src.utils.logger import PrismaLogger

logger = PrismaLogger("URLParser")


# URL regex pattern - handles most common URL formats
URL_PATTERN = re.compile(
    r'https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)',  # path
    re.IGNORECASE
)

# Common file extensions that are not web pages
SKIP_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.exe', '.msi', '.dmg', '.apk',
}


def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.
    
    Args:
        url: String to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def is_scrapeable_url(url: str) -> Tuple[bool, str]:
    """
    Check if URL points to a scrapeable web page.
    
    Args:
        url: URL to check
    
    Returns:
        Tuple of (is_scrapeable, reason)
    """
    if not is_valid_url(url):
        return False, "Invalid URL format"
    
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Check for file extensions
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return False, f"File type {ext} not supported"
    
    # Check for common non-scrapeable paths
    skip_paths = ['/api/', '/graphql', '/feed', '/rss']
    for skip in skip_paths:
        if skip in path.lower():
            return False, f"API/Feed endpoint detected"
    
    return True, "OK"


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all URLs from a text string.
    
    Args:
        text: Text containing URLs
    
    Returns:
        List of unique URLs found
    """
    # Find all URLs
    matches = URL_PATTERN.findall(text)
    
    # Clean up and deduplicate
    urls: Set[str] = set()
    for url in matches:
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?\'")>')
        
        # Normalize
        if not url.startswith('http'):
            url = 'https://' + url
        
        urls.add(url)
    
    result = sorted(list(urls))
    logger.debug(f"Extracted {len(result)} URLs from text")
    return result


def extract_urls_from_lines(lines: List[str]) -> List[str]:
    """
    Extract URLs from a list of lines (one URL per line expected).
    More strict parsing for file input.
    
    Args:
        lines: List of text lines
    
    Returns:
        List of valid URLs
    """
    urls: List[str] = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check if line looks like a URL
        if line.startswith('http://') or line.startswith('https://'):
            if is_valid_url(line):
                urls.append(line)
            else:
                logger.warning(f"Invalid URL skipped: {line[:50]}...")
        else:
            # Try to find URL in the line
            found = extract_urls_from_text(line)
            urls.extend(found)
    
    return urls


def parse_url_file(file_content: str) -> Tuple[List[str], List[str]]:
    """
    Parse a file containing URLs and separate valid from invalid.
    
    Args:
        file_content: Content of URL file
    
    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    lines = file_content.strip().split('\n')
    all_urls = extract_urls_from_lines(lines)
    
    valid_urls: List[str] = []
    invalid_urls: List[str] = []
    
    for url in all_urls:
        is_valid, reason = is_scrapeable_url(url)
        if is_valid:
            valid_urls.append(url)
        else:
            invalid_urls.append(f"{url} ({reason})")
            logger.warning(f"Skipping: {url} - {reason}")
    
    logger.info(f"Parsed {len(valid_urls)} valid URLs, {len(invalid_urls)} skipped")
    return valid_urls, invalid_urls


def get_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL
    
    Returns:
        Domain name (e.g., 'example.com')
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"


def sanitize_filename(url: str, max_length: int = 50) -> str:
    """
    Generate a safe filename from a URL.
    
    Args:
        url: Source URL
        max_length: Maximum filename length
    
    Returns:
        Safe filename string
    """
    # Get domain and path
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Create base name
    if path:
        # Use last path segment
        name = path.split('/')[-1]
        if not name or '.' in name:  # Skip if looks like a file
            name = domain
    else:
        name = domain
    
    # Sanitize: remove invalid chars
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'_+', '_', name)  # Collapse multiple underscores
    name = name.strip('_')
    
    # Truncate if needed
    if len(name) > max_length:
        name = name[:max_length]
    
    return name or "page"


def group_urls_by_domain(urls: List[str]) -> dict[str, List[str]]:
    """
    Group URLs by their domain.
    Useful for rate limiting and organization.
    
    Args:
        urls: List of URLs
    
    Returns:
        Dictionary mapping domain -> list of URLs
    """
    groups: dict[str, List[str]] = {}
    
    for url in urls:
        domain = get_domain(url)
        if domain not in groups:
            groups[domain] = []
        groups[domain].append(url)
    
    return groups
