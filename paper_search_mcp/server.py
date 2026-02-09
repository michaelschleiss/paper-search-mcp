# paper_search_mcp/server.py
from typing import List, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from .academic_platforms.arxiv import ArxivSearcher
from .academic_platforms.pubmed import PubMedSearcher
from .academic_platforms.biorxiv import BioRxivSearcher
from .academic_platforms.medrxiv import MedRxivSearcher
from .academic_platforms.google_scholar import GoogleScholarSearcher
from .academic_platforms.iacr import IACRSearcher
from .academic_platforms.semantic import SemanticSearcher
from .academic_platforms.crossref import CrossRefSearcher
from .academic_platforms.openalex import OpenAlexSearcher

# from .academic_platforms.hub import SciHubSearcher
from .paper import Paper

# Initialize MCP server
mcp = FastMCP("paper_search_server")

# Instances of searchers
arxiv_searcher = ArxivSearcher()
pubmed_searcher = PubMedSearcher()
biorxiv_searcher = BioRxivSearcher()
medrxiv_searcher = MedRxivSearcher()
google_scholar_searcher = GoogleScholarSearcher()
iacr_searcher = IACRSearcher()
semantic_searcher = SemanticSearcher()
crossref_searcher = CrossRefSearcher()
openalex_searcher = OpenAlexSearcher()
# scihub_searcher = SciHubSearcher()


# Asynchronous helper to adapt synchronous searchers
async def async_search(
    searcher, query: str, max_results: int, abstract_limit: int = 200, **kwargs
) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        # Assuming searchers use requests internally; we'll call synchronously for now
        if 'year' in kwargs:
            papers = searcher.search(query, year=kwargs['year'], max_results=max_results)
        else:
            papers = searcher.search(query, max_results=max_results)
        return [paper.to_dict(abstract_limit=abstract_limit) for paper in papers]


# Tool definitions
@mcp.tool()
async def search_arxiv(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from arXiv.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = arxiv_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_pubmed(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from PubMed.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = pubmed_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_biorxiv(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from bioRxiv.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = biorxiv_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_medrxiv(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from medRxiv.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = medrxiv_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_google_scholar(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from Google Scholar.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01'). Only year is used.
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31'). Only year is used.
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = google_scholar_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_iacr(
    query: str, max_results: int = 10, fetch_details: bool = True, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from IACR ePrint Archive.

    Args:
        query: Search query string (e.g., 'cryptography', 'secret sharing').
        max_results: Maximum number of papers to return (default: 10).
        fetch_details: Whether to fetch detailed information for each paper (default: True).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format.
    """
    async with httpx.AsyncClient() as client:
        papers = iacr_searcher.search(query, max_results, fetch_details, date_from=date_from, date_to=date_to)
        return [paper.to_dict(abstract_limit=abstract_limit) for paper in papers] if papers else []


# Unified download/read tools
SEARCHERS = {
    'arxiv': arxiv_searcher,
    'pubmed': pubmed_searcher,
    'biorxiv': biorxiv_searcher,
    'medrxiv': medrxiv_searcher,
    'iacr': iacr_searcher,
    'semantic': semantic_searcher,
    'crossref': crossref_searcher,
    'openalex': openalex_searcher,
}


@mcp.tool()
async def download_paper(paper_id: str, source: str, save_path: str = "./downloads") -> str:
    """Download PDF of a paper from any supported source.

    Args:
        paper_id: Paper identifier (format depends on source).
        source: Source platform (arxiv, pubmed, biorxiv, medrxiv, iacr, semantic, crossref, openalex).
        save_path: Directory to save the PDF (default: './downloads').
    Returns:
        Path to the downloaded PDF file, or error message.
    """
    searcher = SEARCHERS.get(source.lower())
    if not searcher:
        return f"Unknown source: {source}. Supported: {', '.join(SEARCHERS.keys())}"
    try:
        return searcher.download_pdf(paper_id, save_path)
    except NotImplementedError as e:
        return str(e)
    except Exception as e:
        return f"Error downloading paper: {e}"


@mcp.tool()
async def read_paper(paper_id: str, source: str, save_path: str = "./downloads") -> str:
    """Read and extract text content from a paper PDF.

    Args:
        paper_id: Paper identifier (format depends on source).
        source: Source platform (arxiv, pubmed, biorxiv, medrxiv, iacr, semantic, crossref, openalex).
        save_path: Directory where the PDF is/will be saved (default: './downloads').
    Returns:
        str: The extracted text content of the paper, or error message.
    """
    searcher = SEARCHERS.get(source.lower())
    if not searcher:
        return f"Unknown source: {source}. Supported: {', '.join(SEARCHERS.keys())}"
    try:
        return searcher.read_paper(paper_id, save_path)
    except NotImplementedError as e:
        return str(e)
    except Exception as e:
        return f"Error reading paper: {e}"


@mcp.tool()
async def search_semantic(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    year: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from Semantic Scholar.

    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        year: Year filter (e.g., '2019', '2016-2020', '2010-', '-2015').
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01'). Overrides year.
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31'). Overrides year.
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = semantic_searcher.search(
        query, year=year, max_results=max_results,
        date_from=date_from, date_to=date_to
    )
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def search_crossref(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None,
    filter: Optional[str] = None, sort: Optional[str] = None, order: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from CrossRef database.

    Args:
        query: Search query string (e.g., 'machine learning', 'climate change').
        max_results: Maximum number of papers to return (default: 10, max: 1000).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
        filter: CrossRef filter string (e.g., 'has-full-text:true').
        sort: Sort field ('relevance', 'published', 'updated', 'deposited', etc.).
        order: Sort order ('asc' or 'desc').
    Returns:
        List of paper metadata in dictionary format.
    """
    kwargs = {}
    if filter is not None:
        kwargs['filter'] = filter
    if sort is not None:
        kwargs['sort'] = sort
    if order is not None:
        kwargs['order'] = order
    papers = crossref_searcher.search(query, max_results, date_from=date_from, date_to=date_to, **kwargs)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def get_crossref_paper_by_doi(doi: str, abstract_limit: int = 200) -> Dict:
    """Get a specific paper from CrossRef by its DOI.

    Args:
        doi: Digital Object Identifier (e.g., '10.1038/nature12373').
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
    Returns:
        Paper metadata in dictionary format, or empty dict if not found.
    """
    async with httpx.AsyncClient() as client:
        paper = crossref_searcher.get_paper_by_doi(doi)
        return paper.to_dict(abstract_limit=abstract_limit) if paper else {}


@mcp.tool()
async def search_openalex(
    query: str, max_results: int = 10, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from OpenAlex - comprehensive index of 240M+ scholarly works.

    OpenAlex aggregates data from CrossRef, PubMed, arXiv, institutional repositories,
    and more. Results include PDF URLs for open access papers.

    Args:
        query: Search query string (e.g., 'machine learning', 'climate change').
        max_results: Maximum number of papers to return (default: 10, max: 200).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (e.g., '2024-01-01').
        date_to: End date YYYY-MM-DD (e.g., '2024-12-31').
    Returns:
        List of paper metadata in dictionary format. Open access papers include 'pdf' field.
    """
    papers = openalex_searcher.search(query, max_results, date_from=date_from, date_to=date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def get_openalex_work_by_id(openalex_id: str, abstract_limit: int = 200) -> Dict:
    """Get a specific work from OpenAlex by its ID.

    Args:
        openalex_id: OpenAlex work ID (e.g., 'W2741809807').
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
    Returns:
        Paper metadata in dictionary format, or empty dict if not found.
    """
    paper = openalex_searcher.get_work_by_id(openalex_id)
    return paper.to_dict(abstract_limit=abstract_limit) if paper else {}


@mcp.tool()
async def get_openalex_references(
    paper_id: str, max_results: int = 25, abstract_limit: int = 200
) -> List[Dict]:
    """Get papers that a work cites (outgoing references/bibliography).

    Args:
        paper_id: OpenAlex work ID (e.g., 'W2741809807').
        max_results: Maximum number of references to return (default: 25).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
    Returns:
        List of paper metadata for works cited by this paper.
    """
    papers = openalex_searcher.get_references(paper_id, max_results)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def get_openalex_citations(
    paper_id: str, max_results: int = 25, abstract_limit: int = 200
) -> List[Dict]:
    """Get papers that cite a work (incoming citations).

    Args:
        paper_id: OpenAlex work ID (e.g., 'W2741809807').
        max_results: Maximum number of citing papers to return (default: 25).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
    Returns:
        List of paper metadata for works that cite this paper.
    """
    papers = openalex_searcher.get_citing_papers(paper_id, max_results)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


@mcp.tool()
async def get_paper_by_doi(doi: str, abstract_limit: int = 200) -> Dict:
    """Get a paper by its DOI from OpenAlex (with CrossRef fallback).

    Args:
        doi: Digital Object Identifier (e.g., '10.1038/nature12373').
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
    Returns:
        Paper metadata in dictionary format, or empty dict if not found.
    """
    # Try OpenAlex first (has citations, categories)
    paper = openalex_searcher.get_work_by_doi(doi)
    if paper:
        return paper.to_dict(abstract_limit=abstract_limit)

    # Fallback to CrossRef
    paper = crossref_searcher.get_paper_by_doi(doi)
    if paper:
        return paper.to_dict(abstract_limit=abstract_limit)

    return {}


@mcp.tool()
async def search_authors(name: str, max_results: int = 10) -> List[Dict]:
    """Search for authors by name using OpenAlex.

    Args:
        name: Author name to search for (e.g., 'Yann LeCun', 'Hinton').
        max_results: Maximum number of authors to return (default: 10).
    Returns:
        List of author metadata with id, name, works_count, citations, affiliations.
    """
    return openalex_searcher.search_authors(name, max_results)


@mcp.tool()
async def get_author_papers(
    author_id: str, max_results: int = 25, abstract_limit: int = 200,
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict]:
    """Get papers by an author, sorted by citation count.

    Args:
        author_id: OpenAlex author ID (e.g., 'A5015666723').
        max_results: Maximum number of papers to return (default: 25).
        abstract_limit: Max chars for abstract (0=omit, -1=full, default: 200).
        date_from: Start date YYYY-MM-DD (optional).
        date_to: End date YYYY-MM-DD (optional).
    Returns:
        List of paper metadata sorted by citations (highest first).
    """
    papers = openalex_searcher.get_author_papers(author_id, max_results, date_from, date_to)
    return [p.to_dict(abstract_limit=abstract_limit) for p in papers] if papers else []


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
