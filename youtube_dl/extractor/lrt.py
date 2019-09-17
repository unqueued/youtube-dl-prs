# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    unified_timestamp,
    clean_html,
    ExtractorError,
    try_get,
)


class LRTIE(InfoExtractor):
    IE_NAME = 'lrt.lt'
    _VALID_URL = r'https?://(?:www\.)?lrt\.lt/mediateka/irasas/(?P<id>[0-9]+)'
    _TESTS = [{
        # m3u8 download
        'url': 'https://www.lrt.lt/mediateka/irasas/2000078895/loterija-keno-loto',
        # md5 for first 10240 bytes of content
        'md5': '8e6f0121ccacc17d91f98837c66853f0',
        'info_dict': {
            'id': '2000078895',
            'ext': 'mp4',
            'title': u'Loterija \u201eKeno Loto\u201c',
            'description': u'Tira\u017eo nr.: 7993.',
            'timestamp': 1568658420,
            'tags': [u'Loterija \u201eKeno Loto\u201c', u'LRT TELEVIZIJA'],
            'upload_date': '20190916',
        },
    }, {
        # m4a download
        'url': 'https://www.lrt.lt/mediateka/irasas/2000068931/vakaro-pasaka-bebriukas',
        # md5 for first 11297 bytes of content
        'md5': 'f02072fb3c416c1c8f5969ea7b70f53b',
        'info_dict': {
            'id': '2000068931',
            'ext': 'm4a',
            'title': u'Vakaro pasaka. Bebriukas',
            'description': u'Est\u0173 pasaka \u201eBebriukas\u201d. Skaito aktorius Antanas \u0160urna.',
            'timestamp': 1558461780,
            'tags': [u'LRT RADIJAS', u'Vakaro pasaka', u'Bebriukas'],
            'upload_date': '20190521',
        },
    }]

    MEDIA_INFO_URL = 'https://www.lrt.lt/servisai/stream_url/vod/media_info/'
    THUMBNAIL_URL = 'https://www.lrt.lt'
    QUERY_URL = '/mediateka/irasas/'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        media_info = self._download_json(self.MEDIA_INFO_URL, video_id, query={'url': self.QUERY_URL + video_id})

        video_id = try_get(media_info, lambda x: x.get('id'), int)
        if not video_id:
            raise ExtractorError("Unable to fetch media info")

        playlist_item = media_info.get('playlist_item', {})
        file = playlist_item.get('file')
        if not file:
            raise ExtractorError("Media info did not contain m3u8 file url")

        if ".m4a" in file:
            # audio only content
            formats = [{'url': file, 'vcodec': 'none', 'ext': 'm4a'}]
        else:
            formats = self._extract_m3u8_formats(file, video_id, 'mp4', entry_protocol='m3u8_native')

        # adjust media datetime to youtube_dl supported datetime format
        timestamp = unified_timestamp(media_info.get('date').replace('.', '-') + '+02:00')

        return {
            'id': str(video_id).decode('utf-8'),
            'title': playlist_item.get('title', 'unknown title'),
            'formats': formats,
            'thumbnail': self.THUMBNAIL_URL + playlist_item.get('image', '/images/default-img.svg'),
            'description': clean_html(media_info.get('content', 'unknown description')),
            'timestamp': timestamp,
            'tags': [i['name'] for i in media_info.get('tags')] if media_info.get('tags') else [],
        }
