import asyncio

import requests
from bs4 import BeautifulSoup


def get_resume_data(posada, misto, zarplata_ot, zarplata_do, dosvid, place):
    if place == "Work.ua":
        zarplata_ot = int(zarplata_ot)
        zarplata_do = int(zarplata_do)
        dosvid = int(dosvid)

        # фільтри
        if zarplata_ot <= 10000:
            zarplata_ot = "0"
        elif 10000 <= zarplata_ot <= 25000:
            zarplata_ot = "2"
        elif 15000 <= zarplata_ot <= 20000:
            zarplata_ot = "3"
        elif 20000 <= zarplata_ot <= 30000:
            zarplata_ot = "4"
        elif 30000 <= zarplata_ot <= 40000:
            zarplata_ot = "5"
        elif zarplata_ot >= 40000:
            zarplata_ot = "6"
        else:
            zarplata_ot = "0"

        if zarplata_do <= 20000:
            zarplata_do = "4"
        elif zarplata_do <= 30000:
            zarplata_do = "5"
        elif zarplata_do <= 40000:
            zarplata_do = "6"
        elif zarplata_do <= 50000:
            zarplata_do = "7"
        elif zarplata_do <= 100000:
            zarplata_do = "8"
        else:
            zarplata_do = "0"

        if 1 <= dosvid <= 2:
            dosvid = "164"
        elif 2 <= dosvid <= 5:
            dosvid = "165"
        elif 5 <= dosvid:
            dosvid = "166"
        else:
            dosvid = "0"

        url_work_ua = f"https://www.work.ua/resumes-{misto}-{posada}/?salaryfrom={zarplata_ot}&salaryto={zarplata_do}&experience={dosvid}"

        response = requests.get(url_work_ua)
        soup = BeautifulSoup(response.text, "html.parser")

        resumes = []

        resume_blocks = soup.find_all(
            "div",
            class_="card card-hover card-search resume-link card-visited wordwrap",
        )
        if resume_blocks:

            for block in resume_blocks:
                title_element = block.find("h2", class_="mt-0")
                if title_element:
                    points = 0
                    title = title_element.text.strip()
                    link_element = block.find("a", href=True)

                    link = (
                        "https://www.work.ua" + link_element["href"]
                        if link_element
                        else "Немає інформації"
                    )
                    title = title_element.text.strip()

                    price_element = block.find(
                        "p", class_="h5 strong-600 mt-xs mb-0 nowrap"
                    )
                    if price_element:
                        price = price_element.text.strip()
                        points += 1
                    else:
                        price = "Немає інформації"

                    about_element = block.find("p", class_="mt-xs mb-0")
                    if about_element:
                        about = about_element.text.strip()
                        points += 1
                    else:
                        about = "Немає інформації"

                    education_element = block.find(
                        "p", class_="mb-0 mt-xs text-default-7"
                    )
                    if education_element:
                        education = education_element.text.strip()
                        points += 1
                    else:
                        education = "Немає інформації"

                    expirience_element = block.find("ul", class_="mt-lg mb-0")
                    if expirience_element:
                        expirience = expirience_element.text.strip()
                        points += 1
                    else:
                        expirience = "Немає інформації"

                else:
                    continue

                resumes.append(
                    {
                        "title": title,
                        "link": link,
                        "price": price,
                        "about": about,
                        "education": education,
                        "expirience": expirience,
                        "points": points,
                    }
                )

            return resumes

        else:
            return "Не знайдено кандедатів за вказаними критеріями, перевірьте правильність написання"
    elif place == "Robota.ua":
        # url_robota_ua = f"https://www.robota.ua/resumes-{location}-{job_position}/?advs=1&exp={experience}"
        return "Поки в роботі"


async def send_sorted_resumes(
    resumes, message
):  # сортуємо анкети по рівеню заповненості.
    sorted_resumes = sorted(resumes, key=lambda x: x["points"], reverse=True)
    how = len(resumes)
    await message.answer(f"Знайдено {how} анкет")
    await asyncio.sleep(0.5)
    for resume in sorted_resumes:
        await message.answer(
            f"Заголовок: {resume['title']}\n"
            f"Посилання: {resume['link']}\n"
            f"Зарплата: {resume['price']},\n"
            f"Про людину: {resume['about']}\n"
            f"Освіта: {resume['education']}\n"
            f"Досвід: {resume['expirience']}\n"
            f"Рейтинг: {resume['points']}",
            parse_mode="Markdown",
        )
        await asyncio.sleep(0.5)
