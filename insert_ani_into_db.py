from concurrent.futures import ThreadPoolExecutor

import db_adder
import re
import requests

if __name__ == "__main__":
    header = {
        "upgrade-insecure-requests": "1"
    }
    web = requests.get("https://anigod.com/", headers=header)
    text = web.text
    patt = r'<a class="index-link" href="(\/animation\/[\s\S]*?)"[\s\S]*?>[\s\S]*?<\/a>'
    ani_names = ['https://anigod.com/' + ani for ani in re.findall(patt, text)]
    print(ani_names)

    db = db_adder.db_connect()
    with db_adder.Timer() as t, ThreadPoolExecutor(max_workers=20) as executor:
        result = executor.map(lambda url: db_adder.get_ani_data(url), ani_names)
        db.anime.insert(result)

    for ani in db.anime.find():
        print(ani)

    print("걸린 시간:")
    print(t.time)

