from typing import Type

from fastapi import HTTPException, WebSocketException


class BaseHTTPException(HTTPException):
    status_code: int
    status_name: str
    detail: str
    summary: str
    
    def __init__(self, **kwargs):
        if kwargs:
            self.detail = self.detail.format_map(kwargs)
        super().__init__(status_code=self.status_code, detail=self.detail)
    
    @classmethod
    def example(cls) -> dict:
        return {
            cls.summary: {
                "summary": cls.summary,
                "value": {
                    "detail": cls.detail,
                }
            }
        }
    
    @classmethod
    def dict(cls) -> dict:
        return {
            'detail': cls.detail,
        }


class BaseHTTPExceptionsContainer:
    @staticmethod
    def get_responses_dict(exceptions: list[Type[BaseHTTPException]]) -> dict:
        responses_dict = {}
        for exception in exceptions:
            if exception.status_code not in responses_dict.keys():
                responses_dict.update({
                    exception.status_code: {
                        "detail": exception.status_name,
                        "content": {
                            "application/json": {
                                "examples": {
                                }
                            }
                        },
                    }
                })
            responses_dict[exception.status_code]['content']["application/json"]["examples"].update(exception.example())
        return responses_dict


class BaseWebSocketException(WebSocketException):
    status_code: int
    detail: str
    
    def __init__(self, **kwargs):
        if kwargs:
            self.detail = self.detail.format_map(kwargs)
        super().__init__(code=self.status_code, reason=self.detail)
    
    @classmethod
    def dict(cls) -> dict:
        return {
            'detail': cls.detail,
        }


class BaseWebSocketExceptionsContainer:
    ...