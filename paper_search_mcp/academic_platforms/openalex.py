# paper_search_mcp/academic_platforms/openalex.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import requests
import logging
from ..paper import Paper

logger = logging.getLogger(__name__)


class OpenAlexSearcher:
    """Searcher for OpenAlex - a fully open index of scholarly works.

    OpenAlex aggregates data from CrossRef, PubMed, arXiv, institutional
    repositories, and more. It indexes 240M+ works with 50k added daily.
    """

    BASE_URL = "https://api.openalex.org"

    # Polite pool email for faster rate limits
    USER_EMAIL = "paper-search-mcp@example.org"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': f'paper-search-mcp/0.1 (mailto:{self.USER_EMAIL})'
        })

    def search(
        self,
        query: str,
        max_results: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Paper]:
        """Search OpenAlex for academic works.

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 10)
            date_from: Start date in YYYY-MM-DD format (optional)
            date_to: End date in YYYY-MM-DD format (optional)

        Returns:
            List of Paper objects
        """
        try:
            # Build filter string
            filters = [f'title_and_abstract.search:{query}']

            if date_from:
                filters.append(f'from_publication_date:{date_from}')
            if date_to:
                filters.append(f'to_publication_date:{date_to}')

            params = {
                'filter': ','.join(filters),
                'per_page': min(max_results, 200),  # OpenAlex max is 200
                'mailto': self.USER_EMAIL,
                'select': 'id,title,authorships,abstract_inverted_index,doi,publication_date,open_access,primary_location,type,cited_by_count,topics'
            }

            response = self.session.get(f'{self.BASE_URL}/works', params=params)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get('results', []):
                paper = self._parse_work(item)
                if paper:
                    papers.append(paper)

            return papers[:max_results]

        except requests.RequestException as e:
            logger.error(f"OpenAlex search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in OpenAlex search: {e}")
            return []

    def _parse_work(self, item: Dict[str, Any]) -> Optional[Paper]:
        """Parse an OpenAlex work object into a Paper."""
        try:
            # Extract OpenAlex ID (short form)
            openalex_id = item.get('id', '').replace('https://openalex.org/', '')

            # Extract DOI (remove URL prefix if present)
            doi = item.get('doi', '') or ''
            if doi.startswith('https://doi.org/'):
                doi = doi[16:]

            # Extract title
            title = item.get('title', '') or ''

            # Extract authors from authorships
            authors = []
            for authorship in item.get('authorships', []):
                author = authorship.get('author', {})
                name = author.get('display_name', '')
                if name:
                    authors.append(name)

            # Reconstruct abstract from inverted index
            abstract = self._reconstruct_abstract(item.get('abstract_inverted_index'))

            # Extract publication date
            pub_date_str = item.get('publication_date', '')
            published_date = None
            if pub_date_str:
                try:
                    published_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
                except ValueError:
                    try:
                        published_date = datetime.strptime(pub_date_str[:4], '%Y')
                    except ValueError:
                        pass

            # Extract PDF URL from open_access or primary_location
            pdf_url = ''
            open_access = item.get('open_access', {})
            if open_access.get('is_oa'):
                pdf_url = open_access.get('oa_url', '')

            if not pdf_url:
                primary_loc = item.get('primary_location', {}) or {}
                pdf_url = primary_loc.get('pdf_url', '') or ''

            # Extract categories from topics
            categories = []
            for topic in item.get('topics', [])[:3]:  # Limit to top 3
                if topic.get('display_name'):
                    categories.append(topic['display_name'])

            # Work type as category if no topics
            if not categories and item.get('type'):
                categories = [item['type']]

            return Paper(
                paper_id=openalex_id,
                title=title,
                authors=authors,
                abstract=abstract,
                doi=doi,
                published_date=published_date,
                pdf_url=pdf_url,
                url=f"https://openalex.org/{openalex_id}",
                source='openalex',
                categories=categories,
                keywords=[],
                citations=item.get('cited_by_count', 0) or 0
            )

        except Exception as e:
            logger.warning(f"Failed to parse OpenAlex work: {e}")
            return None

    def _reconstruct_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> str:
        """Reconstruct abstract text from OpenAlex inverted index format."""
        if not inverted_index:
            return ''

        try:
            # Build list of (position, word) tuples
            words = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    words.append((pos, word))

            # Sort by position and join
            words.sort(key=lambda x: x[0])
            return ' '.join(word for _, word in words)
        except Exception:
            return ''

    def get_work_by_doi(self, doi: str) -> Optional[Paper]:
        """Get a specific work by DOI.

        Args:
            doi: Digital Object Identifier (e.g., '10.1038/nature12373')

        Returns:
            Paper object if found, None otherwise
        """
        try:
            # Clean DOI - remove URL prefix if present
            if doi.startswith('https://doi.org/'):
                doi = doi[16:]
            elif doi.startswith('http://doi.org/'):
                doi = doi[15:]
            elif doi.startswith('doi:'):
                doi = doi[4:]

            url = f'{self.BASE_URL}/works/https://doi.org/{doi}'
            params = {'mailto': self.USER_EMAIL}

            response = self.session.get(url, params=params)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return self._parse_work(response.json())

        except Exception as e:
            logger.error(f"Error fetching work by DOI {doi}: {e}")
            return None

    def get_work_by_id(self, openalex_id: str) -> Optional[Paper]:
        """Get a specific work by OpenAlex ID.

        Args:
            openalex_id: OpenAlex ID (e.g., 'W2741809807')

        Returns:
            Paper object if found, None otherwise
        """
        try:
            # Ensure proper ID format
            if not openalex_id.startswith('W'):
                openalex_id = f'W{openalex_id}'

            url = f'{self.BASE_URL}/works/{openalex_id}'
            params = {'mailto': self.USER_EMAIL}

            response = self.session.get(url, params=params)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return self._parse_work(response.json())

        except Exception as e:
            logger.error(f"Error fetching OpenAlex work {openalex_id}: {e}")
            return None

    def download_pdf(self, paper_id: str, save_path: str) -> str:
        """Download PDF if available (open access only).

        Args:
            paper_id: OpenAlex ID
            save_path: Directory to save the PDF

        Returns:
            Path to downloaded PDF

        Raises:
            NotImplementedError: If PDF not available
        """
        paper = self.get_work_by_id(paper_id)
        if not paper or not paper.pdf_url:
            raise NotImplementedError(
                "PDF not available. This work may not be open access. "
                "Try accessing via DOI or publisher URL."
            )

        import os
        response = self.session.get(paper.pdf_url)
        response.raise_for_status()

        os.makedirs(save_path, exist_ok=True)
        output_file = f"{save_path}/{paper_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)

        return output_file

    def read_paper(self, paper_id: str, save_path: str = "./downloads") -> str:
        """Read paper content (requires open access PDF).

        Args:
            paper_id: OpenAlex ID
            save_path: Directory for PDF storage

        Returns:
            Extracted text content
        """
        try:
            from PyPDF2 import PdfReader
            import os

            pdf_path = f"{save_path}/{paper_id}.pdf"
            if not os.path.exists(pdf_path):
                pdf_path = self.download_pdf(paper_id, save_path)

            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            return f"Could not read paper: {e}"

    def get_references(self, paper_id: str, max_results: int = 25) -> List[Paper]:
        """Get papers that this work cites (outgoing references).

        Args:
            paper_id: OpenAlex work ID (e.g., 'W2741809807')
            max_results: Maximum number of references to return (default: 25)

        Returns:
            List of Paper objects for referenced works
        """
        try:
            # Ensure proper ID format
            if not paper_id.startswith('W'):
                paper_id = f'W{paper_id}'

            # Get the work to extract referenced_works
            url = f'{self.BASE_URL}/works/{paper_id}'
            params = {'mailto': self.USER_EMAIL}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            referenced_ids = data.get('referenced_works', [])
            if not referenced_ids:
                return []

            # Extract IDs and fetch details
            ref_ids = [r.replace('https://openalex.org/', '') for r in referenced_ids[:max_results]]

            # Batch fetch referenced works
            filter_str = '|'.join(ref_ids)
            params = {
                'filter': f'openalex:{filter_str}',
                'per_page': max_results,
                'sort': 'cited_by_count:desc',
                'mailto': self.USER_EMAIL,
                'select': 'id,title,authorships,abstract_inverted_index,doi,publication_date,open_access,primary_location,cited_by_count,topics'
            }
            response = self.session.get(f'{self.BASE_URL}/works', params=params)
            response.raise_for_status()

            papers = []
            for item in response.json().get('results', []):
                paper = self._parse_work(item)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            logger.error(f"Error fetching references for {paper_id}: {e}")
            return []

    def get_citing_papers(self, paper_id: str, max_results: int = 25) -> List[Paper]:
        """Get papers that cite this work (incoming citations).

        Args:
            paper_id: OpenAlex work ID (e.g., 'W2741809807')
            max_results: Maximum number of citing papers to return (default: 25)

        Returns:
            List of Paper objects for citing works
        """
        try:
            # Ensure proper ID format
            if not paper_id.startswith('W'):
                paper_id = f'W{paper_id}'

            params = {
                'filter': f'cites:{paper_id}',
                'per_page': min(max_results, 200),
                'sort': 'cited_by_count:desc',
                'mailto': self.USER_EMAIL,
                'select': 'id,title,authorships,abstract_inverted_index,doi,publication_date,open_access,primary_location,cited_by_count,topics'
            }

            response = self.session.get(f'{self.BASE_URL}/works', params=params)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get('results', []):
                paper = self._parse_work(item)
                if paper:
                    papers.append(paper)

            return papers[:max_results]

        except Exception as e:
            logger.error(f"Error fetching citing papers for {paper_id}: {e}")
            return []


    def search_authors(self, name: str, max_results: int = 10) -> List[Dict]:
        """Search for authors by name.

        Args:
            name: Author name to search for
            max_results: Maximum number of authors to return (default: 10)

        Returns:
            List of author metadata dictionaries
        """
        try:
            params = {
                'search': name,
                'per_page': min(max_results, 200),
                'mailto': self.USER_EMAIL
            }

            response = self.session.get(f'{self.BASE_URL}/authors', params=params)
            response.raise_for_status()
            data = response.json()

            authors = []
            for a in data.get('results', []):
                author_id = a.get('id', '').replace('https://openalex.org/', '')
                affiliations = [aff.get('display_name') for aff in a.get('affiliations', []) if aff.get('display_name')]

                authors.append({
                    'id': author_id,
                    'name': a.get('display_name', ''),
                    'works_count': a.get('works_count', 0),
                    'citations': a.get('cited_by_count', 0),
                    'affiliations': affiliations[:3] if affiliations else None,
                    'orcid': a.get('orcid', '').replace('https://orcid.org/', '') if a.get('orcid') else None
                })

            # Filter out None values
            for author in authors:
                for key in list(author.keys()):
                    if author[key] is None:
                        del author[key]

            return authors[:max_results]

        except Exception as e:
            logger.error(f"Error searching authors: {e}")
            return []

    def get_author_papers(
        self, author_id: str, max_results: int = 25,
        date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> List[Paper]:
        """Get papers by an author.

        Args:
            author_id: OpenAlex author ID (e.g., 'A5015666723')
            max_results: Maximum number of papers to return (default: 25)
            date_from: Start date in YYYY-MM-DD format (optional)
            date_to: End date in YYYY-MM-DD format (optional)

        Returns:
            List of Paper objects sorted by citation count
        """
        try:
            # Ensure proper ID format
            if not author_id.startswith('A'):
                author_id = f'A{author_id}'

            # Build filter
            filters = [f'author.id:{author_id}']
            if date_from:
                filters.append(f'from_publication_date:{date_from}')
            if date_to:
                filters.append(f'to_publication_date:{date_to}')

            params = {
                'filter': ','.join(filters),
                'per_page': min(max_results, 200),
                'sort': 'cited_by_count:desc',
                'mailto': self.USER_EMAIL,
                'select': 'id,title,authorships,abstract_inverted_index,doi,publication_date,open_access,primary_location,cited_by_count,topics'
            }

            response = self.session.get(f'{self.BASE_URL}/works', params=params)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get('results', []):
                paper = self._parse_work(item)
                if paper:
                    papers.append(paper)

            return papers[:max_results]

        except Exception as e:
            logger.error(f"Error fetching papers for author {author_id}: {e}")
            return []


if __name__ == "__main__":
    # Test OpenAlex searcher
    searcher = OpenAlexSearcher()

    print("Testing OpenAlex search...")
    papers = searcher.search("transformer attention mechanism", max_results=3)

    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title[:60]}...")
        print(f"   ID: {paper.paper_id}")
        print(f"   DOI: {paper.doi}")
        print(f"   PDF: {paper.pdf_url or '(not available)'}")
        print(f"   Citations: {paper.citations}")
