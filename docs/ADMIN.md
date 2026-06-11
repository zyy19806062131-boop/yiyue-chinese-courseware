# Admin Dashboard

Admin URL:

<https://yiyue-chinese-courseware.onrender.com/admin>

Default admin password:

```text
19920811
```

## Set One Password For All Lessons

1. Open `/admin`.
2. Enter the admin password.
3. Type the student-facing password in `统一课程密码`.
4. Click `应用到所有课件`.
5. Click `保存全部`.

The new password takes effect immediately for the running Render service.

## Set A Different Password For One Lesson

1. Open `/admin`.
2. Find the lesson card.
3. Type the new password in `这门课的新密码`.
4. Click `保存全部`.

Leave the field blank when you do not want to change that lesson.

## Persistence Note

The admin dashboard writes to `data/access_rules.json` inside the running Render
instance. On the current free Render setup, changes can reset after a redeploy or
restart because there is no persistent disk/database attached.

For permanent defaults, update `data/access_rules.json` in GitHub with hashed
course passwords and redeploy.
