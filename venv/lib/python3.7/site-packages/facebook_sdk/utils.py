import re

import six
from six.moves.urllib.parse import (
    parse_qs,
    urlencode,
    urlparse,
    urlunparse,
)
from typing import (  # noqa: F401
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Text,
)


def force_slash_prefix(value):  # type: (Text) -> Text
    return '/' + value if not (value and str(value).startswith('/')) else value


def base_graph_url_endpoint(url_to_trim):  # type: (Text) -> Text
    return re.sub(r'^https://.+\.facebook\.com(/v.+?)?/', '/', url_to_trim)


def remove_params_from_url(url, params_to_remove):  # type: (Text, Iterable[Text]) -> Text
    parsed = urlparse(url)
    qd = parse_qs(parsed.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in qd.items() if k not in params_to_remove)
    newurl = urlunparse([
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(filtered, doseq=True),  # query string
        parsed.fragment
    ])

    return newurl


def get_params_from_url(url):  # type: (Text) -> Dict[Text, List[Text]]
    parsed = urlparse(url)
    qd = parse_qs(parsed.query, keep_blank_values=True)
    return qd


def convert_params_to_utf8(params):  # type: (Mapping[Any, Any]) -> Mapping[Any, Any]
    return {
        k: v.encode("utf-8") if isinstance(v, six.text_type) else v
        for k, v in params.items()
    }


def smart_text(value, encoding='utf-8', **kwargs):  # type: (Text, Text, Any) -> Text
    if isinstance(value, six.text_type):
        return value
    elif isinstance(value, six.binary_type):
        return value.decode(encoding=encoding, **kwargs)
    else:
        return six.text_type(value)
