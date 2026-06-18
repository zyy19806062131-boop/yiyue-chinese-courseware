# Yiyue Chinese HTML

This repository hosts the Yiyue Chinese HTML courseware library deployed on Render.

Live site:

- Courseware library: <https://yiyue-chinese-courseware.onrender.com/>
- Admin dashboard: <https://yiyue-chinese-courseware.onrender.com/admin>

The Render service is `yiyue-Chinese-courseware`.

## Short Links

- 端午节 · 龙舟与粽子: <https://yiyue-chinese-courseware.onrender.com/duanwu>
- 苏轼的「重生」: <https://yiyue-chinese-courseware.onrender.com/sushi>
- 谈旅游｜西安旅游: <https://yiyue-chinese-courseware.onrender.com/xian>
- 饭店点餐: <https://yiyue-chinese-courseware.onrender.com/restaurant>
- YCT3 L3 · 我在画画儿呢: <https://yiyue-chinese-courseware.onrender.com/yct3>
- 百家争鸣: <https://yiyue-chinese-courseware.onrender.com/baijia>
- 你好，邻居！: <https://yiyue-chinese-courseware.onrender.com/nihao>
- 7 Topics Speaking Lounge: <https://yiyue-chinese-courseware.onrender.com/tamila>
- HSKK 看图说话 · 进阶刷量: <https://yiyue-chinese-courseware.onrender.com/hskk>
- Niki HSKK 看图说话: <https://yiyue-chinese-courseware.onrender.com/niki>

## What Is Here

- `index.html` is the public courseware library.
- `lessons/` contains the active lesson HTML files linked from the library.
- `assets/` contains lesson media.
- `courseware_server.py` is the Python web server used by Render.
- `server.py` is the Render start entrypoint.
- `data/course_catalog.json` controls the homepage course cards.
- `data/access_rules.json` is the default course access list.
- `docs/` contains operating notes for deployment and course management.

Older top-level HTML files are kept for compatibility and are still protected by
the same password system when listed in `data/access_rules.json`.

## Run Locally

```bash
python server.py
```

Open `http://127.0.0.1:8765/`.

The local admin password defaults to `19920811` unless `ADMIN_PASSWORD` or
`ADMIN_PASSWORD_HASH` is set.

## Deploy On Render

Render uses this command from `render.yaml`:

```bash
python server.py
```

The live service should stay named `yiyue-Chinese-courseware`. Avoid reusing the
old `niki-hskk-*` service names; those were duplicate/legacy services.

## Course Passwords

Go to `/admin`, log in with the admin password, set a unified course password,
click `应用到所有课件`, then click `保存全部`.

For details, see:

- `docs/ADMIN.md`
- `docs/DEPLOYMENT.md`
- `docs/COURSEWARE_INVENTORY.md`
