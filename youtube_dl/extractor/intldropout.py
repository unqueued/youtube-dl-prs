# coding: utf-8
from __future__ import unicode_literals

from .vimeo import VHXEmbedIE

from ..utils import (
    ExtractorError,
    sanitized_Request,
    urlencode_postdata,
    RegexNotFoundError
)

import re

# https://intl.dropout.tv/login
# GET
# authenticity_token

# https://intl.dropout.tv/login
# POST
# authenticity_token
# email
# password
# utf8 ✓


# https://embed.vhx.tv/videos/414462?api=1&autoplay=1&referrer=https%3A%2F%2Fintl.dropout.tv%2Fbrowse&playsinline=1&title=0&context=https%3A%2F%2Fintl.dropout.tv%2Fbrowse&back=Browse&color=feea3b&sharing=1&auth-user-token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1Mzk0NDEwLCJleHAiOjE1NDc0NzA1NDB9._y4H94pKyIOu_GT11qC2SeJnSou6EzN9jI1A-P3tbo8&live=0
# https://vhx-adaptive-hap.akamaized.net/-ctx--user_id,5394410--platform_id,27--video_id,414462--channel_id,55407--plan,standard-/vods3cf/0/amlst:c-55407/v-414462/2220471,2220472,2220473,2220474,2220475,2220476/playlist.m3u8?token=exp=1547481565~acl=/-ctx--user_id,5394410--platform_id,27--video_id,414462--channel_id,55407--plan,standard-/vods3cf/0/amlst:c-55407/v-414462/2220471,2220472,2220473,2220474,2220475,2220476/*~hmac=ceb8508146d2dec2b868db9ca304ec13d54502cca0a7d1cd0def7a85a9ef3962&
# https://api.vhx.tv/videos/414462/files?auth_user_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1Mzk0NDEwLCJleHAiOjE1NDc0NzA1NDB9._y4H94pKyIOu_GT11qC2SeJnSou6EzN9jI1A-P3tbo8&_=1547463565300


class IntlDropoutIE(VHXEmbedIE):
    IE_DESC = 'International Dropout.tv'
    _NETRC_MACHINE = 'intl.dropout.tv'
    _LOGIN_URL = 'https://intl.dropout.tv/login'
    _LOGOUT_URL = 'https://intl.dropout.tv/logout'
    _VALID_URL = r'https://intl\.dropout\.tv/(?P<id>.+)'
    _TEST = {
        'url': 'https://intl.dropout.tv/um-actually/season:1/videos/c-3po-s-origins-hp-lovecraft-the-food-album-with-weird-al-yankovic',
        'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': '42',
            'ext': 'mp4',
            'title': 'Video title goes here',
            'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def _real_initialize(self):
        self._login()

    def _login(self):
        email, password = self._get_login_info()
        if email is None or password is None:
            if self._downloader.params.get('cookiefile') is None:
                raise ExtractorError('No login info available, needed for using %s.' % self.IE_NAME, expected=True)
            return True

        login_page = self._download_webpage(
            self._LOGIN_URL, None,
            note='Downloading login page',
            errnote='unable to fetch login page', fatal=False
        )

        if login_page is False:
            return

        login_form = self._hidden_inputs(login_page)

        login_form.update({
            'passwordless': 0,
            'email': email,
            'password': password
        })

        request = sanitized_Request(
            self._LOGIN_URL, urlencode_postdata(login_form))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        try:
            self._download_webpage(request, None, 'Logging in')
        except Exception:
            print('error')

    def _real_extract(self, url):
        webpage = self._download_webpage(url, None)
        try:
            video = self._html_search_regex(r'<iframe[^>]+"(?P<embed>https://embed.vhx.tv/videos/[0-9]+[^"]*)"[^>]*>', webpage, 'embed')
        except RegexNotFoundError:
            items = re.findall(r'<a href="(?P<url>https://intl.dropout.tv/videos/[^"]+)"', webpage)
            playlist_id = self._search_regex(r'https://intl.dropout.tv/(?P<id>.+)', url, 'id')
            playlist_title = self._html_search_regex(r'<h1 class="[^"]*collection-title[^"]*"[^>]*>(?P<title>[^<]+)<', webpage, 'title')
            return self.playlist_from_matches(items, playlist_id=playlist_id, playlist_title=playlist_title)

        return self.url_result(video)
