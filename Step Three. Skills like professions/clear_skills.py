import json
import sqlite3

import ru_core_news_md


def get_skills() -> set:
    skills = json.load(open("skiils.json", "r"))
    return set([skill['demand_name'].lower().strip() for skill in skills])


def get_waste_skills() -> set:
    skills = json.load(open('waste.json', "r"))
    return set([skill.lower().strip() for skill in skills])


def find_similar_skills(skills: set, waste: set):
    nlp = ru_core_news_md.load()
    for skill in skills:
        doc1 = nlp(skill)
        for waste_skill in waste:
            doc2 = nlp(waste_skill)
            similarity = doc1.similarity(doc2)
            if similarity >= 80:
                print(skill)


def f():
    db = sqlite3.connect("skills.db")
    cursor = db.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS skill(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255),
        confirm INT DEFAULT null,
        is_profession BOOLEAN DEFAULT false
    )""")
    db.commit()

    for skill in skills:
        cursor.execute("INSERT INTO skill(title) VALUES(?)", (skill,))
        db.commit()
    
    db.close()


if __name__ == "__main__":
    skills = get_skills()
    f()
    # waste_skills = get_waste_skills()
    # find_similar_skills(skills=skills, waste=waste_skills)