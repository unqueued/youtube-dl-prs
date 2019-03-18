# coding: utf-8
from __future__ import unicode_literals

from .vimeo import VHXEmbedIE

from ..utils import (
    ExtractorError,
    urlencode_postdata,
)

import re


class IntlDropoutIE(VHXEmbedIE):
    IE_NAME = 'intldropout'
    IE_DESC = 'International Dropout.tv'
    _NETRC_MACHINE = 'intldropouttv'
    _LOGIN_URL = 'https://intl.dropout.tv/login'
    _LOGOUT_URL = 'https://intl.dropout.tv/logout'
    _VALID_URL = r'https://intl\.dropout\.tv/(?:[^/]+/season:[^/]+/)?videos/(?P<id>.+)'
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

        self._download_webpage(self._LOGIN_URL, None, 'Logging in', 'Login failed',
                               expected_status=302,
                               data=urlencode_postdata(login_form),
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def _real_extract(self, url):
        webpage = self._download_webpage(url, None)
        video = self._html_search_regex(r'<iframe[^>]*"(?P<embed>https://embed.vhx.tv/videos/[0-9]+[^"]*)"[^>]*>', webpage, 'embed')
        video_id = self._search_regex(r'https://embed.vhx.tv/videos/(?P<id>[0-9]+)', video, 'id')
        video_title = self._html_search_regex(r'<h1 class="[^"]*video-title[^"]*"[^>]*><strong>(?P<title>[^<]+)<', webpage, 'title', fatal=False)
        return self.url_result(video, video_id=video_id, video_title=video_title)


class IntlDropoutPlaylistIE(IntlDropoutIE):
    IE_NAME = 'intldropout:playlist'
    _VALID_URL = r'https://intl\.dropout\.tv/(?P<id>.+)'
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
            'playlist_count': 22,
            'info_dict': {
                'id': 'new-releases',
                'title': 'New Releases',
            }
        },
        {
            'url': 'https://intl.dropout.tv/troopers/season:2',
            'md5': 'ebcd26ef54f546225e7cb96e79da31cc',
            'playlist_count': 10,
            'info_dict': {
                'id': 'troopers/season:2',
                'title': 'Troopers',
            }
        }
    ]

    @classmethod
    def suitable(cls, url):
        return False if IntlDropoutIE.suitable(url) else super(IntlDropoutPlaylistIE, cls).suitable(url)

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)
        items = re.findall(r'browse-item-title[^>]+>[^<]*<a href="(?P<url>https://intl.dropout.tv/[^/]+/[^"]+)"', webpage)
        playlist_title = self._html_search_regex(r'<h1 class="[^"]*collection-title[^"]*"[^>]*>(?P<title>[^<]+)<', webpage, 'title')
        return self.playlist_from_matches(items, playlist_id=playlist_id, playlist_title=playlist_title)
