# services/book_api_service.py
from logger_setup import logger
from services._base_api_service import _BaseApiService, ITEMS_PER_PAGE
from services.recommendation_config import PERIODS
from exceptions import RateLimitError, ApiError

_GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


class BookApiService(_BaseApiService):

    def fetch(self, period, subject="fiction", page=1, is_turkish=False) -> list:
        if not subject:
            subject = "fiction"

        period_type = PERIODS.get(period, {}).get('type', 'popular')
        order_by = "newest" if period_type == 'new' else "relevance"
        lang_restrict = "tr" if is_turkish else None
        start_index = (page - 1) * ITEMS_PER_PAGE

        params = {
            'q': f"subject:{subject}",
            'startIndex': start_index,
            'maxResults': ITEMS_PER_PAGE,
            'orderBy': order_by,
            'printType': 'books',
        }
        if lang_restrict:
            params['langRestrict'] = lang_restrict

        try:
            response = self._request_with_retry(_GOOGLE_BOOKS_URL, params, timeout=15)
            return self._parse_response(response.json())
        except RateLimitError:
            logger.warning("Kitap API rate limit aşıldı.")
            return []
        except ApiError as e:
            logger.error(f"Google Books API hatası: {e}")
            return []
        except Exception as e:
            logger.error(f"Google Books API beklenmeyen hata: {e}")
            return []

    def _parse_response(self, data: dict) -> list:
        results = []
        seen_titles = set()

        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            title = volume_info.get('title', '')

            if title in seen_titles:
                continue
            seen_titles.add(title)

            image_links = volume_info.get('imageLinks', {})
            img_url = image_links.get('thumbnail') or image_links.get('smallThumbnail')
            if not img_url:
                continue

            img_url = img_url.replace('http://', 'https://')
            authors = volume_info.get('authors', [])
            author_name = ', '.join(authors[:2]) if authors else 'Bilinmiyor'
            published_date = volume_info.get('publishedDate', '')
            year = published_date[:4] if published_date else 'Bilinmiyor'
            rating = (volume_info.get('averageRating') or 0) * 2

            description = volume_info.get('description', '')
            if description:
                description = description[:150] + "..." if len(description) > 150 else description
            else:
                description = f"Yazar: {author_name}"

            results.append({
                'title': title,
                'description': description,
                'rating': rating,
                'image': img_url,
                'date': year,
                'type': 'Kitap',
                'id': item.get('id', title),
            })

            if len(results) >= ITEMS_PER_PAGE:
                break

        return results
