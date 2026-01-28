"""
PRISMA - Web Scraper
====================
Asynchronous web scraping engine using Playwright.
Extracts web content and converts to clean Markdown.

Design Decision:
Using Playwright + html2text instead of Crawl4AI because:
1. More control over browser automation
2. Better error handling
3. Lighter dependency footprint for PyInstaller
4. Easier debugging and maintenance
"""

import asyncio
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import html2text
from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError

try:
    from src.utils.logger import PrismaLogger
    from src.utils.url_parser import sanitize_filename, get_domain
except ImportError:
    # Fallback for direct module testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.utils.logger import PrismaLogger
    from src.utils.url_parser import sanitize_filename, get_domain

logger = PrismaLogger("Scraper")


@dataclass
class ScrapeResult:
    """Result of a single URL scrape operation."""
    
    url: str
    success: bool
    title: str = ""
    markdown: str = ""
    error: str = ""
    content_length: int = 0
    scrape_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScraperConfig:
    """Configuration for the scraper."""
    
    # Browser settings
    headless: bool = True
    timeout: int = 30000  # milliseconds
    wait_for_idle: bool = True
    
    # Content settings
    remove_images: bool = False
    remove_links: bool = False
    ignore_emphasis: bool = False
    body_width: int = 0  # 0 = no wrapping
    
    # Rate limiting
    delay_between_requests: float = 1.0  # seconds
    max_concurrent: int = 3


class WebScraper:
    """
    Asynchronous web scraper for PRISMA.
    Uses Playwright for JavaScript rendering and html2text for conversion.
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper.
        
        Args:
            config: Scraper configuration. Uses defaults if None.
        """
        self.config = config or ScraperConfig()
        self.browser: Optional[Browser] = None
        self.html_converter = self._setup_html_converter()
        
        # Progress callback
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
    
    def _setup_html_converter(self) -> html2text.HTML2Text:
        """Configure the HTML to Markdown converter."""
        h = html2text.HTML2Text()
        
        h.ignore_images = self.config.remove_images
        h.ignore_links = self.config.remove_links
        h.ignore_emphasis = self.config.ignore_emphasis
        h.body_width = self.config.body_width
        h.skip_internal_links = True
        h.inline_links = True
        h.protect_links = True
        h.ignore_tables = False
        h.single_line_break = True
        
        return h
    
    def set_progress_callback(
        self,
        callback: Callable[[int, int, str], None]
    ) -> None:
        """
        Set callback for progress updates.
        
        Args:
            callback: Function(current, total, url) for progress updates
        """
        self._progress_callback = callback
    
    async def _init_browser(self) -> None:
        """Initialize Playwright browser."""
        if self.browser is None:
            logger.info("Starting browser engine...")
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.config.headless,
            )
            logger.success("Browser ready")
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info("Browser closed")
    
    async def _extract_content(self, page: Page) -> Tuple[str, str]:
        """
        Extract title and main content from page.
        
        Args:
            page: Playwright page object
        
        Returns:
            Tuple of (title, html_content)
        """
        # Get page title
        title = await page.title() or "Untitled"
        
        # Try to find main content area
        # Priority: article > main > body
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.article-content',
            '#content',
            'body',
        ]
        
        html_content = ""
        for selector in content_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    html_content = await element.inner_html()
                    if len(html_content) > 500:  # Meaningful content
                        break
            except Exception:
                continue
        
        # Fallback to full body
        if not html_content or len(html_content) < 500:
            html_content = await page.content()
        
        return title, html_content
    
    async def scrape_url(self, url: str) -> ScrapeResult:
        """
        Scrape a single URL and convert to Markdown.
        
        Args:
            url: URL to scrape
        
        Returns:
            ScrapeResult with content or error
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            await self._init_browser()
            
            # Create new page
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            # Navigate to URL
            logger.info(f"Fetching: {url}")
            
            try:
                await page.goto(
                    url,
                    timeout=self.config.timeout,
                    wait_until="domcontentloaded"
                )
                
                # Wait for network to be idle if configured
                if self.config.wait_for_idle:
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass  # Continue even if timeout
                
            except PlaywrightError as e:
                if "net::ERR_" in str(e):
                    raise ConnectionError(f"Network error: {e}")
                raise
            
            # Extract content
            title, html_content = await self._extract_content(page)
            
            # Convert to Markdown
            markdown = self.html_converter.handle(html_content)
            
            # Clean up markdown
            markdown = self._clean_markdown(markdown, title, url)
            
            # Close page
            await context.close()
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            logger.success(f"Scraped: {title[:50]}... ({len(markdown)} chars)")
            
            return ScrapeResult(
                url=url,
                success=True,
                title=title,
                markdown=markdown,
                content_length=len(markdown),
                scrape_time=elapsed,
            )
            
        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            error_msg = str(e)
            logger.error(f"Failed: {url} - {error_msg[:100]}")
            
            return ScrapeResult(
                url=url,
                success=False,
                error=error_msg,
                scrape_time=elapsed,
            )
    
    def _clean_markdown(self, markdown: str, title: str, url: str) -> str:
        """
        Clean and format the markdown output.
        
        Args:
            markdown: Raw markdown from converter
            title: Page title
            url: Source URL
        
        Returns:
            Cleaned markdown with header
        """
        # Remove excessive whitespace
        lines = markdown.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            cleaned_lines.append(line)
            prev_empty = is_empty
        
        markdown = '\n'.join(cleaned_lines).strip()
        
        # Add source header
        header = f"""# {title}

**Source:** {url}  
**Scraped:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

"""
        return header + markdown
    
    async def scrape_urls(
        self,
        urls: List[str],
    ) -> List[ScrapeResult]:
        """
        Scrape multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of ScrapeResult objects
        """
        results: List[ScrapeResult] = []
        total = len(urls)
        
        logger.info(f"Starting batch scrape of {total} URLs")
        
        try:
            await self._init_browser()
            
            for i, url in enumerate(urls):
                # Progress callback
                if self._progress_callback:
                    self._progress_callback(i + 1, total, url)
                
                # Scrape URL
                result = await self.scrape_url(url)
                results.append(result)
                
                # Rate limiting delay (except for last URL)
                if i < total - 1 and self.config.delay_between_requests > 0:
                    await asyncio.sleep(self.config.delay_between_requests)
            
            # Summary
            successful = sum(1 for r in results if r.success)
            logger.success(f"Completed: {successful}/{total} URLs scraped successfully")
            
        finally:
            await self.close()
        
        return results
    
    async def scrape_urls_concurrent(
        self,
        urls: List[str],
    ) -> List[ScrapeResult]:
        """
        Scrape multiple URLs concurrently with semaphore.
        Faster but uses more resources.
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of ScrapeResult objects
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        completed = 0
        total = len(urls)
        
        async def scrape_with_semaphore(url: str) -> ScrapeResult:
            nonlocal completed
            async with semaphore:
                result = await self.scrape_url(url)
                completed += 1
                if self._progress_callback:
                    self._progress_callback(completed, total, url)
                return result
        
        logger.info(f"Starting concurrent scrape of {total} URLs (max {self.config.max_concurrent})")
        
        try:
            await self._init_browser()
            tasks = [scrape_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    processed_results.append(ScrapeResult(
                        url=url,
                        success=False,
                        error=str(result),
                    ))
                else:
                    processed_results.append(result)
            
            successful = sum(1 for r in processed_results if r.success)
            logger.success(f"Completed: {successful}/{total} URLs scraped")
            
            return processed_results
            
        finally:
            await self.close()


# Factory function for easy instantiation
def create_scraper(
    headless: bool = True,
    timeout: int = 30000,
    delay: float = 1.0,
) -> WebScraper:
    """
    Create a configured WebScraper instance.
    
    Args:
        headless: Run browser without UI
        timeout: Page load timeout in ms
        delay: Delay between requests in seconds
    
    Returns:
        Configured WebScraper instance
    """
    config = ScraperConfig(
        headless=headless,
        timeout=timeout,
        delay_between_requests=delay,
    )
    return WebScraper(config)