# Courseware Inventory

## Public Library

`index.html` reads `data/course_catalog.json` and renders the current courseware
library.

| Category | Title | Short URL | Path |
| --- | --- | --- | --- |
| 文化专题 | 端午节 · 龙舟与粽子 | `/duanwu` | `lessons/culture/duanwu-v28.html` |
| 文化专题 | 苏轼的「重生」 | `/sushi` | `lessons/culture/sushi-history.html` |
| 旅游表达 | 谈旅游｜西安旅游 | `/xian` | `lessons/travel/xian-travel.html` |
| 场景口语 | 饭店点餐 | `/restaurant` | `lessons/speaking/restaurant-ordering.html` |
| 少儿中文 | YCT3 L3 · 我在画画儿呢 | `/yct3` | `YCT3_L3_GAME_v6_experience_upgrade.html` |
| 文化专题 | 百家争鸣 | `/baijia` | `baijiazhengmingV24.html` |
| 场景口语 | 你好，邻居！ | `/nihao` | `changjingkouyu/lesson01/lesson01_nihao_neighbor_final_v10_audio_fixed.html` |
| 场景口语 | 7 Topics Speaking Lounge | `/tamila` | `TAMILA%20.html` |
| 场景口语 | HSKK 看图说话 · 进阶刷量 | `/hskk` | `lessons/speaking/hskk-picture-speaking-advanced-02.html.html` |
| 场景口语 | Niki HSKK 看图说话 | `/niki` | `lessons/speaking/niki-hskk-toolbox.html` |

## Access-Controlled Paths

`data/access_rules.json` protects all public library lessons plus legacy wrapper
or redirect paths kept for old links.

The default student password is stored as plaintext for admin display plus a
SHA-256 hash for login checks.

## Add A New HTML Courseware File

1. Put the HTML file under a stable path, preferably `lessons/<category>/`.
2. Put any images/audio under `assets/<lesson-name>/` unless the HTML is fully self-contained.
3. Add the lesson to `data/course_catalog.json` if it should appear on the homepage.
4. Add a short URL in `shortPath`, such as `/sushi`.
5. Add the lesson path to `data/access_rules.json` with the current password and hash.
6. Commit and push to GitHub.
7. Let Render redeploy from `main`.

The admin page can discover HTML files, but committing the catalog and access
rules keeps the intended public library clear in GitHub.
