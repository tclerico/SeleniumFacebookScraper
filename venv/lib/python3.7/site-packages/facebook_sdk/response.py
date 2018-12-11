from copy import copy
import json

from typing import (  # noqa: F401
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    SupportsAbs,
    Text,
    Tuple,
    TypeVar,
    Union,
)

from facebook_sdk.constants import METHOD_GET
from facebook_sdk.exceptions import (
    FacebookResponseException,
    FacebookSDKException,
)
from facebook_sdk.request import (  # noqa: F401
    FacebookBatchRequest,
    FacebookRequest,
)
from facebook_sdk.utils import (
    base_graph_url_endpoint,
    smart_text,
)


if TYPE_CHECKING:
    from mypy_extensions import TypedDict
    ResponseRecord = TypedDict('ResponseRecord', {
        'name': Text,
        'response': 'FacebookResponse'
    })

T = TypeVar('T', bound=FacebookRequest)


class BaseResponse(Generic[T]):

    def __init__(self, request):  # type (T) -> None
        self.request = request


class ResponsePaginationMixin(object):
    def next_page_request(self):  # type: () -> Optional[FacebookRequest]
        """ Return a FacebookRequest for the next page of the current Response

        :return: a FacebookRequest
        """
        return self._build_pagination_request('next')

    def previous_page_request(self):  # type: () -> Optional[FacebookRequest]
        """ Return a FacebookRequest for the previous page of the current Response

        :return: a FacebookRequest
        """
        return self._build_pagination_request('previous')

    def _build_pagination_request(self, direction):  # type: (Text) -> Optional[FacebookRequest]
        if self.request.method != METHOD_GET:  # type: ignore
            raise FacebookSDKException('You can only paginate on a GET request.', 720)

        pagination_url = self.json_body.get('paging', {}).get(direction)  # type: ignore

        request = None
        if pagination_url:
            request = copy(self.request)  # type: ignore
            request.endpoint = base_graph_url_endpoint(pagination_url)

        return request


class FacebookResponse(ResponsePaginationMixin, BaseResponse[FacebookRequest]):
    """ A Facebook Response

    """

    def __init__(
        self,
        request,  # type: FacebookRequest
        http_status_code,  # type: int
        body,  # type: Text
        headers=None,  # type: Optional[Dict[Text, Text]]
    ):
        # type: (...) -> None
        super(FacebookResponse, self).__init__(request)
        self.body = body
        self.http_status_code = http_status_code
        self.headers = headers

        self._parse_body()

        if self.is_error:
            self._build_exception()

    @property
    def is_error(self):  # type: () -> bool
        """ Check if the response is an error."""
        return 'error' in self.json_body

    def _parse_body(self):  # type: () -> None
        """ Parse the raw response to json."""
        try:
            self.json_body = json.loads(smart_text(self.body))  # type: Dict
        except Exception:
            self.json_body = {}

    def raiseException(self):  # type: () -> None
        """ Raise the FacebookSDKException."""
        raise self.exception

    def _build_exception(self):  # type: () -> None
        self.exception = FacebookResponseException.create(response=self)   # type: FacebookResponseException


class FacebookBatchResponse(FacebookResponse, BaseResponse[FacebookBatchRequest]):
    """ A Facebook Batch Response"""

    def __init__(self, batch_request, batch_response):
        # type: (FacebookBatchRequest, FacebookResponse) -> None
        super(FacebookBatchResponse, self).__init__(
            request=batch_request,
            body=batch_response.body,
            http_status_code=batch_response.http_status_code,
            headers=batch_response.headers
        )

        self.responses = self.build_responses(self.json_body)  # type: List[ResponseRecord]

    def build_responses(self, json_body):  # type: (Dict) -> List[ResponseRecord]
        """ Parse the json_body to a set of FacebookResponse.

        :param json_body: parsed batch response
        """
        responses = []  # type: List[ResponseRecord]

        for index, response in enumerate(json_body):
            request_name = self.request.requests[index]['name']
            request = self.request.requests[index]['request']

            body = response.get('body')
            code = response.get('code')
            headers = response.get('headers')

            responses.insert(
                index,
                {
                    'name': request_name,
                    'response': FacebookResponse(
                        request=request,
                        body=body,
                        headers=headers,
                        http_status_code=code,
                    ),
                }
            )

        return responses

    def __iter__(self):  # type: () -> Iterable[ResponseRecord]
        return iter(self.responses)
