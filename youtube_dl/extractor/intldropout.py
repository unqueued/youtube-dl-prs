# coding: utf-8
from __future__ import unicode_literals

from .vimeo import VHXEmbedIE

from ..utils import (
    ExtractorError,
    sanitized_Request,
    urlencode_postdata,
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
    IE_NAME = 'intldropout'
    IE_DESC = 'International Dropout.tv'
    _NETRC_MACHINE = 'intl.dropout.tv'
    _LOGIN_URL = 'https://intl.dropout.tv/login'
    _LOGOUT_URL = 'https://intl.dropout.tv/logout'
    _VALID_URL = r'https://intl\.dropout\.tv/([^/]+/season:[^/]+/)?videos/(?P<id>.+)'
    _TESTS = [
        {
            'url': 'https://intl.dropout.tv/um-actually/season:1/videos/c-3po-s-origins-hp-lovecraft-the-food-album-with-weird-al-yankovic',
            'md5': '8beaac579b6ba762f63cd452fd28dcce',
            'info_dict': {
                'id': '397785',
                'ext': 'mp4',
                'title': "C-3PO's Origins, HP Lovecraft, the Food Album (with Weird Al Yankovic)",
                'thumbnail': r're:^https://vhx.imgix.net/.*\.jpg$',
                'description': 'Caldwell Tanner, Siobhan Thompson, and Nate Dern inspect guns and review the Diagon Alley bar scene.',
                'upload_date': '20181206',
                'timestamp': 1544117975,
            }
        },
        {
            'url': 'https://intl.dropout.tv/videos/um-actually-behind-the-scenes',
            'md5': 'b974927cd563423fe50945dbfdbb894c',
            'info_dict': {
                'id': '397943',
                'ext': 'mp4',
                'title': 'Um, Actually: Behind the Scenes',
                'thumbnail': r're:^https://vhx.imgix.net/.*\.jpg$',
                'description': 'What does it take to stump the nerdy? Mike Trapp and team pull back the curtain.',
                'upload_date': '20181206',
                'timestamp': 1544118409,
            }
        }
    ]

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
            errnote='unable to fetch login page', fatal=False,
            expected_status=200
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
            self._download_webpage(request, None, 'Logging in', expected_status=302)
        except Exception:
            raise ExtractorError(
                'Unable to login',
                expected=True)

    def _real_extract(self, url):
        try:
            webpage = self._download_webpage(url, None, expected_status=200)
        except Exception:
            raise ExtractorError(
                'Unable to fetch page',
                expected=True)
        video = self._html_search_regex(r'<iframe[^>]*"(?P<embed>https://embed.vhx.tv/videos/[0-9]+[^"]*)"[^>]*>', webpage, 'embed')
        video_id = self._search_regex(r'https://embed.vhx.tv/videos/(?P<id>[0-9]+)', video, 'id')
        video_title = self._html_search_regex(r'<h1 class="[^"]*video-title[^"]*"[^>]*>(<strong>)?(?P<title>[^<]+)<', webpage, 'title')
        return self.url_result(video, video_id=video_id, video_title=video_title)


class IntlDropoutPlaylistIE(IntlDropoutIE):
    IE_NAME = 'intldropout:playlist'
    _VALID_URL = r'^https://intl\.dropout\.tv/(?P<id>[^/]+(/season:[^/]+)?)$'
    _TESTS = [
        {
            'url': 'https://intl.dropout.tv/um-actually-the-web-series',
            'md5': 'ebcd26ef54f546225e7cb96e79da31cc',
            'playlist_count': 9,
            'info_dict': {
                'id': 'um-actually-the-web-series',
                'title': 'Um, Actually: The Web Series',
            }
        },
        {
            'url': 'https://intl.dropout.tv/new-releases',
            'md5': 'ebcd26ef54f546225e7cb96e79da31cc',
            'playlist_count': 21,
            'info_dict': {
                'id': 'new-releases',
                'title': 'New Releases',
            }
        }
    ]

    def _real_extract(self, url):
        try:
            webpage = self._download_webpage(url, None, expected_status=200)
        except Exception:
            raise ExtractorError(
                'Unable to fetch page',
                expected=True)
        items = re.findall(r'<a href="(?P<url>https://intl.dropout.tv/[^/]+/[^"]+)"', webpage)
        playlist_id = self._search_regex(r'https://intl.dropout.tv/(?P<id>.+)', url, 'id')
        playlist_title = self._html_search_regex(r'<h1 class="[^"]*collection-title[^"]*"[^>]*>(?P<title>[^<]+)<', webpage, 'title')
        return self.playlist_from_matches(items, playlist_id=playlist_id, playlist_title=playlist_title)
