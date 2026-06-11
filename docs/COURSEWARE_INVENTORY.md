# Courseware Inventory

## Public Library

`index.html` reads `data/course_catalog.json` and renders the current courseware
library.

| Category | Title | Path |
| --- | --- | --- |
| 文化专题 | 端午节 · 龙舟与粽子 | `lessons/culture/duanwu-v28.html` |
| 旅游表达 | 谈旅游｜西安旅游 | `lessons/travel/xian-travel.html` |
| 场景口语 | 饭店点餐 | `lessons/speaking/restaurant-ordering.html` |
| 少儿中文 | YCT3 L3 · 我在画画儿呢 | `YCT3_L3_GAME_v6_experience_upgrade.html` |
| 文化专题 | 百家争鸣 | `baijiazhengmingV24.html` |
| 场景口语 | 你好，邻居！ | `changjingkouyu/lesson01/lesson01_nihao_neighbor_final_v10_audio_fixed.html` |
| 场景口语 | 7 Topics Speaking Lounge | `TAMILA%20.html` |
| 场景口语 | HSKK 看图说话 · 进阶刷量 | `lessons/speaking/hskk-picture-speaking-advanced-02.html.html` |
| 场景口语 | Niki HSKK 看图说话 | `lessons/speaking/niki-hskk-toolbox.html` |

## Access-Controlled Paths

`data/access_rules.json` protects all public library lessons plus legacy wrapper
or redirect paths kept for old links.

The default student password is stored as a SHA-256 hash, not plaintext.

## Add A New HTML Courseware File

1. Put the HTML file under a stable path, preferably `lessons/<category>/`.
2. Put any images/audio under `assets/<lesson-name>/` unless the HTML is fully self-contained.
3. Add the lesson to `data/course_catalog.json` if it should appear on the homepage.
4. Add the lesson path to `data/access_rules.json` with the current password hash.
5. Commit and push to GitHub.
6. Let Render redeploy from `main`.

The admin page can discover HTML files, but committing the catalog and access
rules keeps the intended public library clear in GitHub.
