# Courseware Inventory

## Public Library

`index.html` links to the current public courseware cards:

| Title | Path |
| --- | --- |
| 端午节 · 龙舟与粽子 | `lessons/culture/duanwu-v28.html` |
| 谈旅游｜西安旅游 | `lessons/travel/xian-travel.html` |
| 饭店点餐 | `lessons/speaking/restaurant-ordering.html` |

## Access-Controlled Lessons

`data/access_rules.json` currently registers:

| Title | Path |
| --- | --- |
| 端午节 · 龙舟与粽子 | `lessons/culture/duanwu-v28.html` |
| 点餐与饮食文化｜Cinematic CFL v5 | `lessons/speaking/restaurant-ordering.html` |
| 谈旅游｜新目标汉语口语 2 · Unit 6 | `lessons/travel/xian-travel.html` |
| 声调旋律训练器 · Tone Melody Trainer | `tone_trainer.html` |
| 声调旋律训练器 · Tone Melody Trainer | `tone_trainer_voiced.html` |
| 林安的西安推荐 | `travel_story_lesson.html` |

## Add A New HTML Courseware File

1. Put the HTML file under `lessons/<category>/`.
2. Put any images/audio under `assets/<lesson-name>/`.
3. Add a card to `index.html`.
4. Add the lesson path to `data/access_rules.json`.
5. Commit and push to GitHub.
6. Let Render redeploy from `main`.

The server also auto-discovers HTML files for the admin page, but committing the
lesson to `data/access_rules.json` keeps the intended title and default access
settings clear in GitHub.
