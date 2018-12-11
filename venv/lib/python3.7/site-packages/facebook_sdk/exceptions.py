from typing import (  # noqa: F401
    TYPE_CHECKING,
    Any,
    Text,
    Tuple,
    Type,
    Union,
)


if TYPE_CHECKING:
    from facebook_sdk.response import FacebookResponse  # noqa: F401


SUB_CODE_AUTH_EXCEPTION_CODES = (458, 459, 460, 463, 464, 467)
SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES = (1363030, 1363030, 1363037, 1363033, 1363021, 1363041)
AUTH_EXCEPTION_CODES = (100, 102, 190)
SERVER_EXCEPTION_CODES = (1, 2)
THROTTLE_EXCEPTION_CODES = (4, 17, 341)
CLIENT_EXCEPTION_CODES = (506,)


class FacebookSDKException(Exception):
    pass


class FacebookRequestException(FacebookSDKException):
    pass


class FacebookResponseException(FacebookSDKException):
    def __init__(self, response, code, message, **kwargs):
        # type: (FacebookResponse, int, Text,  Any) -> None
        super(FacebookResponseException, self).__init__(code, message)
        self.response = response
        self.code = code
        self.message = message

        self.error_subcode = kwargs.get('error_subcode')
        self.error_user_msg = kwargs.get('error_user_msg', '')
        self.error_user_title = kwargs.get('error_user_title', '')
        self.type = kwargs.get('error_type', '')

    @staticmethod
    def create(response):
        # type: (FacebookResponse) -> FacebookResponseException
        data = response.json_body
        error = (
            data
            if data.get('error', {}).get('code') is None and data.get('code') is not None
            else data.get('error', {})
        )

        code = error.get('code', -1)
        subcode = error.get('error_subcode', -1)
        message = error.get('message', 'Unknown error from Graph.')
        exception = FacebookOtherException  # type: Type[FacebookResponseException]
        if (
            subcode in SUB_CODE_AUTH_EXCEPTION_CODES or
            code in AUTH_EXCEPTION_CODES or
            error.get('type') == 'OAuthException'
        ):
            exception = FacebookAuthenticationException
        elif subcode in SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES:
            exception = FacebookResumableUploadException
        elif code in SERVER_EXCEPTION_CODES:
            exception = FacebookServerException
        elif code in THROTTLE_EXCEPTION_CODES:
            exception = FacebookThrottleException
        elif code == 10 or 200 <= code <= 299:
            exception = FacebookAuthorizationException

        return exception(
            response=response,
            code=code,
            message=message,
            error_subcode=subcode,
            error_user_title=error.get('error_user_title', ''),
            error_user_msg=error.get('error_user_msg', ''),
            error_type=error.get('type', ''),
        )


class FacebookAuthenticationException(FacebookResponseException):
    pass


class FacebookResumableUploadException(FacebookResponseException):
    pass


class FacebookServerException(FacebookResponseException):
    pass


class FacebookThrottleException(FacebookResponseException):
    pass


class FacebookClientException(FacebookResponseException):
    pass


class FacebookAuthorizationException(FacebookResponseException):
    pass


class FacebookOtherException(FacebookResponseException):
    pass
