from typing import List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import random
from ..paper import Paper
import logging

logger = logging.getLogger(__name__)

class PaperSource:
    """Abstract base class for paper sources"""
    def search(self, query: str, **kwargs) -> List[Paper]:
        raise NotImplementedError

    def download_pdf(self, paper_id: str, save_path: str) -> str:
        raise NotImplementedError

    def read_paper(self, paper_id: str, save_path: str) -> str:
        raise NotImplementedError
    

class GoogleScholarSearcher(PaperSource):
    """Custom implementation of Google Scholar paper search"""
    
    SCHOLAR_URL = "https://scholar.google.com/scholar"
    BROWSERS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]

    def __init__(self):
        self._setup_session()

    def _setup_session(self):
        """Initialize session with random user agent"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.BROWSERS),
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        })

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from publication info"""
        for word in text.split():
            if word.isdigit() and 1900 <= int(word) <= datetime.now().year:
                return int(word)
        return None

    def _extract_cluster_id(self, item) -> Optional[str]:
        """Extract Google Scholar cluster ID from result item"""
        import re
        # Look for cluster/cites ID in the links (gs_fl div contains "Cited by", "All versions", etc.)
        links_div = item.find('div', class_='gs_fl')
        if links_div:
            for a in links_div.find_all('a', href=True):
                href = a['href']
                # Match cluster=ID or cites=ID
                match = re.search(r'(?:cluster|cites)=(\d+)', href)
                if match:
                    return match.group(1)

        # Also check data-cid attribute on the result container
        if item.get('data-cid'):
            return item['data-cid']

        return None

    def _extract_citations(self, item) -> int:
        """Extract citation count from result item"""
        import re
        links_div = item.find('div', class_='gs_fl')
        if links_div:
            for a in links_div.find_all('a'):
                text = a.get_text()
                if 'Cited by' in text:
                    match = re.search(r'Cited by (\d+)', text)
                    if match:
                        return int(match.group(1))
        return 0

    def _parse_paper(self, item) -> Optional[Paper]:
        """Parse single paper entry from HTML"""
        try:
            # Extract main paper elements
            title_elem = item.find('h3', class_='gs_rt')
            info_elem = item.find('div', class_='gs_a')
            abstract_elem = item.find('div', class_='gs_rs')

            if not title_elem or not info_elem:
                return None

            # Process title and URL
            title = title_elem.get_text(strip=True).replace('[PDF]', '').replace('[HTML]', '')
            link = title_elem.find('a', href=True)
            url = link['href'] if link else ''

            # Extract cluster ID (Google Scholar's unique paper identifier)
            cluster_id = self._extract_cluster_id(item)

            # Fallback to URL hash if no cluster ID found
            paper_id = cluster_id if cluster_id else f"gs_{abs(hash(url))}"

            # Process author info
            info_text = info_elem.get_text()
            authors = [a.strip() for a in info_text.split('-')[0].split(',')]
            year = self._extract_year(info_text)

            # Extract citation count
            citations = self._extract_citations(item)

            # Create paper object
            return Paper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract_elem.get_text() if abstract_elem else "",
                url=url,
                pdf_url="",
                published_date=datetime(year, 1, 1) if year else None,
                updated_date=None,
                source="google_scholar",
                categories=[],
                keywords=[],
                doi="",
                citations=citations
            )
        except Exception as e:
            logger.warning(f"Failed to parse paper: {e}")
            return None

    def search(self, query: str, max_results: int = 10, date_from: str = None, date_to: str = None) -> List[Paper]:
        """
        Search Google Scholar with custom parameters

        Args:
            query: Search query string
            max_results: Maximum number of papers to return
            date_from: Start date in YYYY-MM-DD format (only year is used)
            date_to: End date in YYYY-MM-DD format (only year is used)
        """
        papers = []
        start = 0
        results_per_page = min(10, max_results)

        while len(papers) < max_results:
            try:
                # Construct search parameters
                params = {
                    'q': query,
                    'start': start,
                    'hl': 'en',
                    'as_sdt': '0,5'  # Include articles and citations
                }

                # Add year filters if provided (extract year from YYYY-MM-DD format)
                if date_from:
                    try:
                        year_from = int(date_from.split('-')[0])
                        params['as_ylo'] = year_from
                    except (ValueError, IndexError):
                        logger.warning(f"Invalid date_from format: {date_from}")

                if date_to:
                    try:
                        year_to = int(date_to.split('-')[0])
                        params['as_yhi'] = year_to
                    except (ValueError, IndexError):
                        logger.warning(f"Invalid date_to format: {date_to}")

                # Make request with random delay
                time.sleep(random.uniform(1.0, 3.0))
                response = self.session.get(self.SCHOLAR_URL, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Search failed with status {response.status_code}")
                    break

                # Parse results
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('div', class_='gs_ri')

                if not results:
                    break

                # Process each result
                for item in results:
                    if len(papers) >= max_results:
                        break
                        
                    paper = self._parse_paper(item)
                    if paper:
                        papers.append(paper)

                start += results_per_page

            except Exception as e:
                logger.error(f"Search error: {e}")
                break

        return papers[:max_results]

    def download_pdf(self, paper_id: str, save_path: str) -> str:
        """
        Google Scholar doesn't support direct PDF downloads
        
        Raises:
            NotImplementedError: Always raises this error
        """
        raise NotImplementedError(
            "Google Scholar doesn't provide direct PDF downloads. "
            "Please use the paper URL to access the publisher's website."
        )

    def read_paper(self, paper_id: str, save_path: str = "./downloads") -> str:
        """
        Google Scholar doesn't support direct paper reading
        
        Returns:
            str: Message indicating the feature is not supported
        """
        return (
            "Google Scholar doesn't support direct paper reading. "
            "Please use the paper URL to access the full text on the publisher's website."
        )

if __name__ == "__main__":
    # Test Google Scholar searcher
    searcher = GoogleScholarSearcher()
    
    print("Testing search functionality...")
    query = "machine learning"
    max_results = 5
    
    try:
        papers = searcher.search(query, max_results=max_results)
        print(f"\nFound {len(papers)} papers for query '{query}':")
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors)}")
            print(f"   Citations: {paper.citations}")
            print(f"   URL: {paper.url}")
    except Exception as e:
        print(f"Error during search: {e}")