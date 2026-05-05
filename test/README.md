# test

`test` 文件夹用于存放 CheckMate 开发阶段的调试脚本。

这些脚本主要用于测试数据库、防丢失、防篡改、备份恢复、宠物经验、任务归档等功能。

注意：  
这里的脚本是开发者调试工具，不是正式用户功能。运行前建议先彻底退出 CheckMate，避免程序仍在托盘后台运行并占用数据库。

---

## 当前测试脚本

```text
test/
├── test_tamper_db.py
├── test_restore_latest_backup.py
├── test_trust_current_database.py
└── README.md
```

---

## 运行前准备

建议所有测试脚本都从项目根目录运行。

项目根目录示例：

```text
C:\Users\xiany\Desktop\CheckMate
```

运行方式示例：

```bat
python test\test_tamper_db.py
```

如果使用虚拟环境：

```bat
.venv\Scripts\python.exe test\test_tamper_db.py
```

---

## 数据库位置

CheckMate 当前正式数据库位于：

```text
%LOCALAPPDATA%\CheckMate\data\checkmate.db
```

实际示例：

```text
C:\Users\用户名\AppData\Local\CheckMate\data\checkmate.db
```

测试脚本不应该再写死旧路径：

```text
CheckMate\data\checkmate.db
```

而应该统一使用：

```python
from data_guard.paths import get_database_path

DB_PATH = get_database_path()
```

---

## 1. test_tamper_db.py

### 作用

模拟外部篡改数据库。

该脚本会直接修改当前数据库中的一条任务标题，用来测试 CheckMate 的完整性校验机制是否能发现数据库被外部修改。

通常会把任务标题从：

```text
测试任务
```

改成：

```text
测试任务_tampered
```

如果多次运行，会继续追加：

```text
测试任务_tampered_tampered
```

---

### 使用场景

用于测试：

- `integrity.json` 是否能检测数据库变化
- 启动时是否能触发数据安全警告
- 是否会生成 `suspicious_checkmate_xxx.db`
- 检测到异常后是否不会刷新完整性记录

---

### 推荐测试流程

```text
1. 正常启动 CheckMate
2. 添加一个测试任务
3. 从托盘彻底退出 CheckMate
4. 运行 test_tamper_db.py
5. 再次启动 CheckMate
6. 检查是否弹出数据安全提醒
7. 检查是否生成 suspicious 备份
```

运行命令：

```bat
python test\test_tamper_db.py
```

---

### 预期结果

运行脚本后，终端应输出类似：

```text
数据库路径： C:\Users\用户名\AppData\Local\CheckMate\data\checkmate.db
已篡改数据库：
任务 ID： 20
原标题： 测试任务
新标题： 测试任务_tampered
```

再次启动 CheckMate 后，应触发数据安全提醒，并在备份目录生成：

```text
suspicious_checkmate_xxx.db
```

---

## 2. test_restore_latest_backup.py

### 作用

从最近一次自动备份中恢复数据库。

该脚本会查找：

```text
%LOCALAPPDATA%\CheckMate\data_backups\
```

中的最近一个：

```text
auto_checkmate_xxx.db
```

然后用它恢复当前数据库：

```text
%LOCALAPPDATA%\CheckMate\data\checkmate.db
```

恢复前，脚本会自动把当前数据库备份为：

```text
before_restore_checkmate_xxx.db
```

这样即使恢复错了，也能保留恢复前的数据现场。

---

### 使用场景

用于测试：

- 自动备份是否可用
- 是否能从最近备份恢复
- 恢复前是否生成 `before_restore` 备份
- 恢复后是否可以重新信任数据库
- 恢复后再次启动 CheckMate 是否不再报警

---

### 推荐测试流程

```text
1. 正常启动 CheckMate，确保已经生成 auto 备份
2. 从托盘彻底退出 CheckMate
3. 运行 test_tamper_db.py 篡改数据库
4. 再次启动 CheckMate，确认触发数据安全警告
5. 从托盘彻底退出 CheckMate
6. 运行 test_restore_latest_backup.py
7. 再次启动 CheckMate
8. 确认不再出现完整性警告
```

运行命令：

```bat
python test\test_restore_latest_backup.py
```

---

### 预期结果

终端应输出类似：

```text
恢复结果：
success: True
message: 数据库已从备份恢复。
backup_path: ...
database_path: ...
before_restore_backup: ...

已信任恢复后的数据库：
database_path: ...
sha256: ...
updated_at: ...
version: 1
```

恢复后再次启动 CheckMate，应该不再触发完整性警告。

---

## 3. test_trust_current_database.py

### 作用

强制信任当前数据库。

该脚本会把当前的：

```text
checkmate.db
```

作为正确数据库，并重新生成或更新：

```text
integrity.json
```

也就是说，它会刷新当前数据库的 SHA256 校验记录。

---

### 使用场景

用于调试时手动确认当前数据是正确的，例如：

- 手动修改数据库后，确认修改结果没问题
- 清空或重建数据库后，不想继续触发完整性警告
- 调试任务、习惯、宠物经验、历史记录时，想强制刷新校验记录
- 数据库被检测为 suspicious 后，确认当前数据库可以继续作为可信数据

---

### 风险提醒

这个脚本会把当前数据库登记为可信状态。

如果当前数据库其实已经被错误修改，运行该脚本后，CheckMate 会认为它是正常数据。

所以建议只在开发和调试阶段使用，不要作为正式用户功能直接暴露。

---

### 普通运行

运行命令：

```bat
python test\test_trust_current_database.py
```

脚本会要求输入：

```text
YES
```

只有输入完全一致的 `YES` 才会继续执行。

---

### 跳过确认直接运行

```bat
python test\test_trust_current_database.py --yes
```

---

### 推荐测试流程

```text
1. 从托盘彻底退出 CheckMate
2. 手动修改数据库，或运行 test_tamper_db.py
3. 运行 test_trust_current_database.py
4. 再次启动 CheckMate
5. 确认不再出现完整性警告
```

---

### 预期结果

终端应输出类似：

```text
当前数据库路径：
C:\Users\用户名\AppData\Local\CheckMate\data\checkmate.db

完整性记录路径：
C:\Users\用户名\AppData\Local\CheckMate\data_backups\integrity.json

已强制信任当前数据库，并更新 integrity.json。

新的完整性记录：
database_path: ...
sha256: ...
updated_at: ...
version: 1
```

---

## 常见问题

### 1. ModuleNotFoundError: No module named 'data_guard'

如果测试脚本直接放在 `test/` 目录里运行，可能找不到项目根目录下的模块。

测试脚本开头应包含：

```python
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
```

然后再导入项目模块：

```python
from data_guard.paths import get_database_path
```

---

### 2. unable to open database file

常见原因：

- 数据库路径写错
- 还在使用旧路径 `CheckMate/data/checkmate.db`
- CheckMate 没有初始化数据库
- 程序仍在后台运行并占用数据库

解决方法：

```text
1. 确认使用 get_database_path()
2. 正常启动一次 CheckMate，让程序创建数据库
3. 从托盘彻底退出 CheckMate
4. 再运行测试脚本
```

---

### 3. 修改数据库后没有触发警告

可能原因：

- 修改后运行了 `test_trust_current_database.py`
- 程序正常操作后刷新了完整性记录
- 修改的不是正式数据库
- 打开的仍是旧路径下的数据库

请确认当前正式数据库路径：

```python
from data_guard.paths import get_database_path

print(get_database_path())
```

---

## 建议测试顺序

完整测试数据安全链路时，建议按下面顺序：

```text
1. 正常启动 CheckMate
2. 添加一个测试任务
3. 从托盘彻底退出 CheckMate
4. 运行 test_tamper_db.py
5. 再次启动 CheckMate，确认报警
6. 从托盘彻底退出 CheckMate
7. 运行 test_restore_latest_backup.py
8. 再次启动 CheckMate，确认不报警
9. 如需手动信任当前数据，运行 test_trust_current_database.py
```

---

## 注意事项

- 测试前建议从托盘彻底退出 CheckMate。
- 不要只关闭主窗口，因为程序可能仍在后台运行。
- 测试脚本只用于开发调试。
- 不建议把这些测试脚本作为正式用户入口。
- 正式用户的数据管理功能后续应放在设置页面中，例如：
  - 打开数据文件夹
  - 打开备份文件夹
  - 立即备份
  - 从备份恢复
  - 信任当前数据库

---

## 后续可补充的测试脚本

后续可以继续增加：

```text
test_archive_expired_tasks.py
test_pet_growth.py
test_repeat_reminder.py
test_data_guard_cleanup.py
```

其中：

| 文件                            | 作用                                      |
| ------------------------------- | ----------------------------------------- |
| `test_archive_expired_tasks.py` | 测试一次性任务第二天自动归档              |
| `test_pet_growth.py`            | 测试完成任务后宠物经验增长                |
| `test_repeat_reminder.py`       | 测试重复提醒任务逻辑                      |
| `test_data_guard_cleanup.py`    | 测试 suspicious / before_restore 备份清理 |