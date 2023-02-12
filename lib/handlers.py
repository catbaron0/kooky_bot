import logging
from datetime import datetime
from typing import Optional, Dict

from khl import Message
from khl.card import CardMessage, Card, Module, Element, Types, Color
import requests
import wikipedia as wiki
from pypinyin import pinyin
import openai

from lib.utils import create_kook_image


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(filename='white.log', encoding='utf-8', mode='w')
ch = logging.StreamHandler()
fh.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
ch.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(fh)
logger.addHandler(ch)


class GptImgCMD:
    def __init__(self, bot, api_key: str):
        self.bot = bot
        self.name = 'img'
        self.api_key = api_key

    async def __call__(self, msg: Message, prompt: str):
        if not prompt.strip():
            return
        # if not words.strip() and msg.quote and msg.quote.content:
        #     words = msg.quote.content
        try:
            await msg.reply("Drawing...")
            openai.api_key = self.api_key
            data = openai.Image.create(
                prompt=prompt,
                size="512x512",
                n=4
                # user=msg.author_id
            )["data"]
            print(data)

            card = Card()
            for dt in data:
                url = dt['url']
                image = await create_kook_image(self.bot, url)
                # if image_group is None:
                #     image_group = Module.ImageGroup(Element.Image(src=image))
                # else:
                #     image_group.append(Element.Image(src=image))
                try:
                    image_group.append(Element.Image(src=image))
                except NameError:
                    image_group = Module.ImageGroup(Element.Image(src=image))
            card.append(image_group)
            reply = CardMessage(card)
        except Exception as e:
            reply = f"Error! \n```\n{e}\n```"
        await msg.reply(reply)


class GptCMD:
    def __init__(self, api_key: str):
        self.name = 'gpt'
        self.api_key = api_key

    async def __call__(self, msg: Message, prompt: str):
        if not prompt.strip():
            return
        # if not words.strip() and msg.quote and msg.quote.content:
        #     words = msg.quote.content
        try:
            openai.api_key = self.api_key
            reply = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2048,
                stream=False,
                user=msg.author_id
            )["choices"][0]["text"].strip()
        except Exception as e:
            reply = f"Error! \n```\n{e}\n```"
        await msg.reply(reply)


class PinyinCMD:
    def __init__(self):
        self.name = 'py'
        self.usage = '中文内容'
        self.brief = 'Label pinyin to inputs Chinese.'
        self.description = self.brief

    @staticmethod
    def words2pinyin(words):
        pys = pinyin(words, heteronym=False, errors=lambda x: list(x))
        word_py = ""
        for i, w in enumerate(words):
            py = '/'.join(pys[i])
            if py == w:
                word_py += w
            else:
                word_py += f"{w}({py})"
        return word_py

    async def __call__(self, msg: Message, words: str):
        if not words.strip():
            return
        # if not words.strip() and msg.quote and msg.quote.content:
        #     words = msg.quote.content
        reply = self.words2pinyin(words)
        await msg.reply(reply)


class WikiCMD:
    def __init__(self, bot, lang="zh"):
        self.wiki = wiki
        self.lang = lang
        self.wiki.set_lang(lang)
        self.bot = bot

        self.name = 'wiki'
        self.usage = 'QUERY'
        self.brief = 'Search for input query from wikipedia.zh'
        self.description = self.brief

    async def generate_reply(self, item) -> str:
        try:
            page = self.wiki.page(item)
            title = page.title
            context = page.summary
            link = page.url
            images = page.images
        except wiki.PageError:
            title = "Error"
            context = f'No wikipedia page for "{item}"'
            link = ""
            images = []
        except wiki.DisambiguationError as e:
            options = ", ".join(e.options)
            ambi = f"[{item}] may refer to: \n {options}.\n"
            ambi += f"Here is the intro about **{e.options[0]}**: \n"
            page = self.wiki.page(e.options[0])
            title = page.title
            context = ambi + page.summary
            link = page.url
            images = page.images

        card = Card(
            Module.Header(title),
            Module.Section(text=context),
            Module.Divider(),
        )
        if images:
            img_urls = list()
            for src in images[1: 9]:
                img_url = await create_kook_image(self.bot, src)
                if img_url:
                    img_urls.append(img_url)
            if img_urls:
                image_group = Module.ImageGroup(Element.Image(src=img_urls[0]))
                for img_url in img_urls[1:]:
                    image_group.append(Element.Image(src=img_url))
                card.append(image_group)
        if link:
            card.append(
                Module.ActionGroup(Element.Button('More', link, Types.Click.LINK))
            )
        emb = CardMessage(card)
        return emb

    async def __call__(self, msg, query: str):
        if not query.strip():
            return
        try:
            reply = await self.generate_reply(query)
        except Exception as e:
            print(e)
            msg_text = f'Failed to fetch wikipedia page for "{query}"'
            reply = CardMessage(Card(Module.Section(text=msg_text)))

        await msg.reply(reply)


class InkRadio:
    def __init__(self, bot):
        self.bot = bot

        self.name = 'spl'
        self.usage = ''
        self.brief = ''
        self.description = self.brief

        self.card_color = {
            "coop-grouping": Color(249, 55, 40),
            "x": Color(34, 212, 135),
            "regular": Color(197, 248, 30),
            "fest": Color(197, 248, 30),
            "bankara-challenge": Color(239, 50, 16),
            "bankara-open": Color(239, 50, 16),
        }

        self.card_theme = {
            "coop-grouping": "warning",
            "x": "success",
            "regular": "success",
            "fest": "success",
            "bankara-challenge": "warning",
            "bankara-open": "warning"
        }

        self.text_theme = {
            "coop-grouping": "warning",
            "x": "success",
            "regular": "success",
            "fest": "success",
            "bankara-challenge": "warning",
            "bankara-open": "warning"
        }

        self.mode_alias = {
            "coop-grouping": ["coop-grouping", '打工', 'sr', 'dg', 'dagong'],
            "x": ["x"],
            "regular": ["regular", "涂地", 'td', 'tudi'],
            "fest": ["fest", "jd"],
            "bankara-challenge": ["bankara-challenge", "challenge", "挑战", "tz", "真格挑战", "zgtz"],
            "bankara-open": ["bankara-challenge", "开放", "kf", "open", "真格开放", "zgkf"],
        }

        self.rule_cn = {
            'TURF_WAR': '常规涂地',
            'CLAM': '真格蛤蜊',
            'GOAL': '真格鱼虎',
            'LOFT': '真格推塔',
            'AREA': '真格区域'
        }

        self.mode_cn = {
            "coop-grouping": "打工模式",
            "x": "X挑战",
            "regular": "常规涂地",
            "fest": "祭典",
            "bankara-challenge": "真格挑战",
            "bankara-open": "真格开放"
        }

        self.stage_cn = {
            "ユノハナ大渓谷": "温泉大峡谷",
            "ゴンズイ地区": "鳗鲶区",
            "ヤガラ市場": "烟管鱼市场",
            "マテガイ放水路": "竹蛏疏洪道",
            "ナメロウ金属": "鱼肉碎金属",
            "クサヤ温泉": "臭鱼干温泉",
            "ヒラメが丘団地": "比目鱼住宅区",
            "マサバ海峡大橋": "真鲭跨海大桥",
            "キンメダイ美術館": "金眼鲷美术馆",
            "マヒマヒリゾート＆スパ": "鬼头刀SPA度假区",
            "海女美術大学": "海女美术大学",
            "チョウザメ造船": "鲟鱼造船厂",
            "ザトウマーケット": "座头购物中心",
            "スメーシーワールド": "醋饭海洋世界"
        }

    def alias_to_mode(self, mode: str) -> str:
        if mode in self.mode_alias:
            return mode
        for k, v in self.mode_alias.items():
            if mode in v:
                return k
        return None

    @staticmethod
    def get_stage_info(mode: str, schedule: str) -> Optional[Dict]:
        url = f"https://spla3.yuu26.com/api/{mode}/{schedule}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    async def generate_card(self, mode: str, schedule: str) -> CardMessage:
        mode = self.alias_to_mode(mode)
        assert mode and mode in self.mode_alias, "模式名错误！"
        print(mode)
        mode_name = self.mode_cn.get(mode, mode)
        # color = self.card_color[mode]

        if schedule in ["n", "next"]:
            schedule = "next"
        else:
            schedule = "now"
        info = self.get_stage_info(mode, schedule)
        if info is None or 'results' not in info:
            return None
        results = info['results'][0]

        title = f"当前的 {mode_name} 场地在这里!"
        if schedule == "next":
            title = f"接下来的 {mode_name} 场地在这里!"
        card = Card(Module.Header(title), theme=self.card_theme[mode])

        theme = self.text_theme[mode]
        if 'rule' in results:
            try:
                rule = results['rule']['key']
                rule_name = self.rule_cn.get(rule, rule)
            except Exception:
                rule_name = "FEST???"
            if results.get('is_fest', False):
                mode_name += "(FEST!!!)"
            card.append(
                Module.Section(
                    Element.Text(f"**(font){rule_name}(font)[{theme}]**", type=Types.Text.KMD)
                )
            )

        if results.get("is_big_run", False):
            card.append(
                Module.Section(
                    Element.Text(f"**(font)BIG RUN!(font)[{theme}]**", type=Types.Text.KMD)
                )
            )

        if 'end_time' in results:
            end_time = datetime.strptime(results['end_time'], "%Y-%m-%dT%H:%M:%S+09:00")
            card.append(Module.Countdown(end_time, mode=Types.CountdownMode.DAY))

        card.append(Module.Divider())
        stages = results.get('stages', [])
        if stages:
            for stage in stages:
                name = stage['name']
                name = self.stage_cn.get(name, name)
                image = await create_kook_image(self.bot, stage['image'])
                card.append(
                    Module.Section(
                        Element.Text(f"**(font){name}(font)[{theme}]**", type=Types.Text.KMD)
                    )
                )
                card.append(Module.Container(Element.Image(image)))

        if 'stage' in results and results is not None:
            stage = results['stage']
            name = stage['name']
            name = self.stage_cn.get(name, name)
            image = await create_kook_image(self.bot, stage['image'])
            card.append(
                Module.Section(
                    Element.Text(f"(font){name}(font)[{theme}]", type=Types.Text.KMD)
                )
            )
            card.append(Module.Container(Element.Image(image)))

        image_group = None
        for weapon in results.get('weapons', []):
            image = await create_kook_image(self.bot, weapon['image'])
            if image_group is None:
                image_group = Module.ImageGroup(Element.Image(src=image))
            else:
                image_group.append(Element.Image(src=image))
        if image_group is not None:
            card.append(image_group)
        return CardMessage(card)

    async def __call__(self, msg, mode: str = "", schedule: str = 'now'):
        # reply = await self.generate_card(mode, schedule)
        try:
            reply = await self.generate_card(mode, schedule)
        except Exception as e:
            await msg.reply(f"查询失败: {e}!")
            return

        if reply is None:
            await msg.reply("查询失败！")
        else:
            await msg.reply(reply)
