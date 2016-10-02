import re
import requests


def get_anigod_list(main_url):
    main_url = re.sub(r"\/\d+$", "", main_url)
    main_url = re.sub(r"\/$", "", main_url)
    patt = r'<a class="table-link" href="([\s\S]*?)">[\s\S]*?<\/a>'
    cnt = 1
    ani_list = []
    header = {
        "upgrade-insecure-requests": "1"
    }
    while True:
        url = main_url + "/" + str(cnt)
        text = requests.get(url, headers=header).text
        while not text:
            print("error")
            text = requests.get(url, headers=header).text
        aniSubUrl = re.findall(patt, str(text))
        if aniSubUrl:
            ani_list += aniSubUrl
            print(ani_list)
            cnt += 1
        else:
            break
    ani_list = ["https://anigod.com" + sub for sub in ani_list]
    return ani_list


if __name__ == "__main__":
    main_url = "https://anigod.com/animation/%EC%9D%80%ED%95%98%EC%B2%A0%EB%8F%84-999-1608"
    result = get_anigod_list(main_url)
    print(result)
