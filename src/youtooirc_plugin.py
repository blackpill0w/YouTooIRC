# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

def url_is_youtube_playilst(url: str) -> bool:
    return -1 != url.find('/playlist')

def get_title_from_youtube_video(soup: BeautifulSoup) -> str:
    title_end_idx = soup.get_text().rfind('-')
    title = soup.get_text()[:title_end_idx]
    return title

def get_title_from_youtube_playlist(soup: BeautifulSoup) -> str:
    title_tag = soup.contents[1].find('title')
    title = ''
    if not title_tag:
        title = "<Oops, I couldn't get the title>"
    else:
        title_end_idx = soup.get_text().rfind('-')
        title = title_tag.get_text()[:title_end_idx]
    return title

@irc3.plugin
class YtPlugin:
    YT_URL_REGEX = "((?:https?:)?\\/\\/)?((?:www|m)\\.)?((?:youtube(-nocookie)?\\.com|youtu.be))(\\/(?:[\\w\\-]+\\?v=|embed\\/|live\\/|v\\/)?)([\\w\\-]+)(\\S+)?"

    def __init__(self, bot):
        self.bot = bot
        self.yt_reg = re.compile(YtPlugin.YT_URL_REGEX)

    @irc3.event(irc3.rfc.JOIN)
    def say_hi(self, mask, channel, **kw):
        """Say hi when someone join a channel"""
        # if mask.nick != self.bot.nick:
        #     self.bot.privmsg(channel, 'Hi faggot %s!' % mask.nick)
        # else:
        #     self.bot.privmsg(channel, 'Hi fags!')
        return None

    @command(permission='basic_perms')
    def echo(self, mask, target, args):
        """Echo

            %%echo <message>...
        """
        # TODO: This bitch shits itself when the message has unclosed '/" for some retarded reason.
        #       I probably will remove this though.
        yield ' '.join(args['<message>'])

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_msg(self, mask, event, target, data):
        read_least_one_elem = False
        yt_links_iter = self.yt_reg.finditer(data)
        for match in yt_links_iter:
            if not read_least_one_elem:
                self.bot.privmsg(target, f"Found YouTube links:")
                read_least_one_elem = True
            url = data[match.start() : match.end()]
            if not url.startswith("http"):
                url = f"http://{url}"
            page = urlopen(url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            title = ''
            if url_is_youtube_playilst(url):
                title = get_title_from_youtube_playlist(soup)
            else:
                title = get_title_from_youtube_video(soup)
            self.bot.privmsg(target, f"\t - Link 1: {title} ==> {url}")
