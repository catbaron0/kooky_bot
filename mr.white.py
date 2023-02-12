import sys
import json


import lib.handlers as handlers
from khl import Bot, Message


with open(sys.argv[1], 'r', encoding='utf-8') as f:
    config = json.load(f)
# init Bot
bot = Bot(token=config['token'])
openai_key = config['openai_key']


py_hdl = handlers.PinyinCMD()
gpt_hdl = handlers.GptCMD(openai_key)
wiki_hdl = handlers.WikiCMD(bot)
spl_hdl = handlers.InkRadio(bot)
gpt_img_hdl = handlers.GptImgCMD(bot, openai_key)


@bot.command(name='hello')
async def hello(msg: Message):
    await msg.reply("world")


@bot.command(name=gpt_img_hdl.name)
async def img(msg: Message, *args):
    prompt = ' '.join(args)
    await gpt_img_hdl(msg, prompt)


@bot.command(name=gpt_hdl.name)
async def gpt(msg: Message, *args):
    prompt = ' '.join(args)
    await gpt_hdl(msg, prompt)


@bot.command(
    name=py_hdl.name,
    desc=py_hdl.description,
    help=py_hdl.usage
)
async def pinyin(msg: Message, *args):
    words = ' '.join(args)
    await py_hdl(msg, words)


@bot.command(
    name=wiki_hdl.name,
    desc=wiki_hdl.description,
    help=wiki_hdl.usage
)
async def wiki(msg: Message, *args):
    words = ' '.join(args)
    await wiki_hdl(msg, words)


@bot.command(
    name=spl_hdl.name,
    desc=spl_hdl.description,
    help=spl_hdl.usage
)
async def spl(msg: Message, mode: str = "", schedule: str = "now"):
    if not mode.strip():
        for mode in spl_hdl.mode_alias:
            await spl_hdl(msg, mode, schedule)
    else:
        await spl_hdl(msg, mode, schedule)


@bot.command(name="td", aliases=["涂地", "tudi"])
async def td(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "td", schedule)


@bot.command(name="jd", aliases=["涂地", "tudi", "fest"])
async def jd(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "fest", schedule)


@bot.command(name="zg", aliases=["真格", "zhenge"])
async def zg(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "zgtz", schedule)
    await spl_hdl(msg, "zgkf", schedule)


@bot.command(name="kf", aliases=["真格开放", "开放", "open"])
async def kf(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "kf", schedule)


@bot.command(name="tz", aliases=["真格挑战", "挑战", "challenge"])
async def tz(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "tz", schedule)


@bot.command(name="dg", aliases=["打工"])
async def dg(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "dg", schedule)


@bot.command(name="x")
async def x(msg: Message, schedule: str = "now"):
    await spl_hdl(msg, "x", schedule)


bot.run()
