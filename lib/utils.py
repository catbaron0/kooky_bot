import requests
from pathlib import Path


async def create_kook_image(bot, path: str) -> str:
    '''
    Upload image to kook server.


    :param bot: The kook bot instance.
    :param path: The path or url to an image.
    '''
    # if path is url, download the image first
    if path.startswith("http"):
        fn = Path(path.split("?")[0]).name
        if fn.endswith("svg"):
            return ""
        req = requests.get(path)
        if req.status_code != 200:
            return ""
        img = req.content

        path = f"/tmp/{fn}"
        with open(path, 'wb') as f:
            f.write(img)
    return await bot.create_asset(path)
