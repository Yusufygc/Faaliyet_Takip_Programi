# exceptions.py


class AppError(Exception):
    """Tüm uygulama hatalarının temel sınıfı."""


class DatabaseError(AppError):
    """Veritabanı işlemlerinde oluşan hatalar."""


class ApiError(AppError):
    """Harici API çağrılarında oluşan hatalar."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(ApiError):
    """API rate limit aşımı (HTTP 429)."""
    def __init__(self, url=""):
        super().__init__(f"Rate limit aşıldı: {url}", status_code=429)
        self.url = url


class ValidationError(AppError):
    """Kullanıcı girdisi veya iş kuralı doğrulama hataları."""
