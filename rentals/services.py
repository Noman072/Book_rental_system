"""
Service module for interacting with OpenLibrary API.
"""
import requests
from typing import Optional, Dict, Any


class OpenLibraryService:
    """
    Service class for fetching book information from OpenLibrary API.
    Uses a two-step process:
    1. Search for book by title/name
    2. Fetch edition details to get accurate page count
    """
    BASE_URL = "https://openlibrary.org"
    
    @staticmethod
    def search_book_by_title(title: str) -> Optional[Dict[str, Any]]:
        """
        Search for a book by title using OpenLibrary API.
        
        This method:
        1. Searches for the book by name
        2. Extracts the first edition key
        3. Fetches edition details to get accurate page count
        
        Args:
            title: Book title to search for
            
        Returns:
            Dictionary containing book information or None if not found
        """
        try:
            # Step 1: Search for book by name
            search_url = f"{OpenLibraryService.BASE_URL}/search.json"
            params = {'q': title}
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('docs') or len(data['docs']) == 0:
                return None
            
            # Get first match
            book_data = data['docs'][0]
            
            # Step 2: Try to get page count from edition details
            # Try multiple sources for edition keys
            edition_keys = (
                book_data.get('edition_key', []) or 
                ([book_data['cover_edition_key']] if book_data.get('cover_edition_key') else [])
            )
            number_of_pages = 0
            
            if edition_keys:
                # Try multiple editions until we find one with page count
                for edition_key in edition_keys[:3]:  # Try first 3 editions
                    page_count = OpenLibraryService._get_edition_page_count(edition_key)
                    if page_count and page_count > 0:
                        number_of_pages = page_count
                        break
            
            # Fallback to search result page count if edition lookup fails
            if number_of_pages == 0:
                number_of_pages = (
                    book_data.get('number_of_pages_median') or 
                    book_data.get('number_of_pages') or 
                    0
                )
            
            # Parse and return book information
            return OpenLibraryService._parse_book_data(book_data, number_of_pages)
            
        except Exception as e:
            print(f"Error fetching book data: {e}")
            return None
    
    @staticmethod
    def _get_edition_page_count(edition_key: str) -> Optional[int]:
        """
        Fetch page count from OpenLibrary Books API using edition key.
        
        Args:
            edition_key: Edition identifier (e.g., 'OL12345M')
            
        Returns:
            Number of pages or None if not found
        """
        try:
            # Call Books API with edition key
            books_url = f"{OpenLibraryService.BASE_URL}/api/books"
            params = {
                'bibkeys': f'OLID:{edition_key}',
                'format': 'json',
                'jscmd': 'data'
            }
            
            response = requests.get(books_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract page count from response
            edition_data = data.get(f'OLID:{edition_key}', {})
            page_count = edition_data.get('number_of_pages')
            
            if page_count:
                return int(page_count)
            
            return None
            
        except Exception as e:
            print(f"Error fetching edition details for {edition_key}: {e}")
            return None
    
    @staticmethod
    def _parse_book_data(book_data: Dict[str, Any], number_of_pages: int) -> Dict[str, Any]:
        """
        Parse book data from OpenLibrary API response.
        
        Args:
            book_data: Raw book data from Search API
            number_of_pages: Page count from edition details or search result
            
        Returns:
            Parsed book information dictionary
        """
        # Get first author if available
        author = None
        if book_data.get('author_name'):
            author = book_data['author_name'][0]
        
        # Get ISBN if available
        isbn = None
        if book_data.get('isbn'):
            isbn = book_data['isbn'][0]
        
        # Get OpenLibrary key
        openlibrary_key = book_data.get('key', '')
        
        # Get cover image URL
        cover_image_url = None
        if book_data.get('cover_i'):
            cover_id = book_data['cover_i']
            cover_image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        
        return {
            'title': book_data.get('title', 'Unknown Title'),
            'author': author,
            'isbn': isbn,
            'number_of_pages': int(number_of_pages) if number_of_pages else 0,
            'cover_image_url': cover_image_url,
            'openlibrary_key': openlibrary_key,
        }
    
    @staticmethod
    def get_book_details(openlibrary_key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed book information using OpenLibrary key.
        
        Args:
            openlibrary_key: OpenLibrary work key
            
        Returns:
            Dictionary containing detailed book information or None if not found
        """
        try:
            url = f"{OpenLibraryService.BASE_URL}{openlibrary_key}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching book details: {e}")
            return None
