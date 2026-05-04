# data_guard

`data_guard` 是 CheckMate 的数据安全模块，用于保护本地数据库，降低数据丢失和被外部篡改的风险。

当前模块的目标不是实现绝对安全，而是做到：

- 数据不容易因为误删、覆盖、更新而丢失
- 数据库被外部修改后能够被检测出来
- 检测到异常时不会把可疑数据库误认为正常数据库
- 出问题后可以从备份中恢复数据
- 程序更新或替换 release 文件夹时，用户数据不会被一起删除

---

## 目录结构

```text
data_guard/
├── __init__.py
├── paths.py
├── backup_manager.py
├── integrity_manager.py
├── migration_manager.py
├── startup_guard.py
└── README.md
```

---

## 当前数据存储位置

CheckMate 的正式用户数据不再保存在项目目录下，而是保存在 Windows 当前用户的本地应用数据目录中。

Windows 默认路径：

```text
%LOCALAPPDATA%\CheckMate\
```

实际示例：

```text
C:\Users\用户名\AppData\Local\CheckMate\
```

当前数据目录结构：

```text
%LOCALAPPDATA%\CheckMate\
├── data/
│   └── checkmate.db
└── data_backups/
    ├── auto_checkmate_xxx.db
    ├── suspicious_checkmate_xxx.db
    ├── before_restore_checkmate_xxx.db
    ├── integrity.json
    └── migration_done.txt
```

其中：

| 文件 / 目录                       | 说明                                       |
| --------------------------------- | ------------------------------------------ |
| `data/checkmate.db`               | CheckMate 的主数据库                       |
| `data_backups/`                   | 数据库备份与完整性记录目录                 |
| `auto_checkmate_xxx.db`           | 正常启动时生成的自动备份                   |
| `suspicious_checkmate_xxx.db`     | 检测到数据库疑似被外部修改时生成的可疑备份 |
| `before_restore_checkmate_xxx.db` | 从备份恢复前，对当前数据库做的保护性备份   |
| `integrity.json`                  | 数据库完整性校验记录                       |
| `migration_done.txt`              | 数据迁移检查记录                           |

---

## 为什么要迁移到 AppData

旧版本数据库位于项目目录：

```text
CheckMate/data/checkmate.db
```

这种方式在开发阶段方便，但正式发布后有风险：

```text
用户删除 release 文件夹
↓
data/checkmate.db 也被一起删除
↓
任务、打卡记录、宠物进度全部丢失
```

迁移到 AppData 后，程序文件和用户数据分离：

```text
release/CheckMate/
├── CheckMate.exe
├── _internal/
└── assets/

%LOCALAPPDATA%/CheckMate/
├── data/
│   └── checkmate.db
└── data_backups/
```

这样即使用户更新、删除或替换程序目录，用户数据仍然保留。

---

## 文件说明

### `paths.py`

统一管理数据安全相关路径。

主要负责：

- 获取程序目录
- 获取用户数据目录
- 获取数据库路径
- 获取备份目录
- 获取完整性校验文件路径
- 获取旧版本数据库路径
- 创建必要的数据目录

当前正式数据库路径：

```text
%LOCALAPPDATA%\CheckMate\data\checkmate.db
```

当前备份目录：

```text
%LOCALAPPDATA%\CheckMate\data_backups\
```

后续如果需要修改数据存储位置，应优先修改 `paths.py`。

---

### `migration_manager.py`

负责旧数据库迁移。

旧版本数据库路径：

```text
CheckMate/data/checkmate.db
```

新版本数据库路径：

```text
%LOCALAPPDATA%\CheckMate\data\checkmate.db
```

迁移策略：

```text
如果新数据库已经存在：
    不覆盖新数据库

如果新数据库不存在，但旧数据库存在：
    复制旧数据库到 AppData 用户数据目录

如果旧备份目录存在：
    复制旧备份文件到新的 data_backups 目录

旧 integrity.json 不直接迁移：
    因为数据库路径已经变化，启动后会重新生成完整性记录
```

迁移完成后，会生成：

```text
%LOCALAPPDATA%\CheckMate\data_backups\migration_done.txt
```

这个文件用于记录迁移检查结果，方便排查问题。

---

### `backup_manager.py`

负责数据库备份与恢复。

当前支持：

- 启动时自动备份数据库
- 创建可疑数据库备份
- 创建恢复前保护性备份
- 列出备份文件
- 获取最近一次自动备份
- 从指定备份恢复数据库
- 从最近一次自动备份恢复数据库
- 清理旧的自动备份

备份文件前缀说明：

| 前缀              | 含义                                     |
| ----------------- | ---------------------------------------- |
| `auto_`           | 正常启动时生成的自动备份                 |
| `manual_`         | 手动备份，预留给后续设置页面             |
| `suspicious_`     | 检测到数据库疑似被外部修改时生成         |
| `before_restore_` | 从备份恢复前，对当前数据库做的保护性备份 |

---

### `integrity_manager.py`

负责数据库完整性校验。

基本流程：

```text
计算 checkmate.db 的 SHA256
↓
保存到 integrity.json
↓
下次启动时重新计算
↓
如果 hash 不一致，说明数据库可能被外部修改或损坏
```

如果检测到异常，会锁定完整性记录更新，避免把可疑数据库重新登记为正常数据库。

`integrity.json` 示例：

```json
{
    "database_path": "C:\\Users\\用户名\\AppData\\Local\\CheckMate\\data\\checkmate.db",
    "sha256": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "updated_at": "2026-05-04 20:04:54",
    "version": 1
}
```

---

### `startup_guard.py`

负责程序启动时的数据安全检查流程。

主函数：

```python
run_startup_data_guard()
```

推荐在 `main_window.py` 中这样使用：

```python
migration_result = migrate_legacy_database_if_needed()
database.init_db()
self.data_guard_result = run_startup_data_guard()
```

启动时会根据数据库状态执行不同操作：

```text
数据库正常：
    自动备份
    刷新完整性记录

首次运行 / 没有完整性记录：
    创建完整性记录
    自动备份

数据库疑似被篡改：
    打印警告
    创建 suspicious 可疑备份
    锁定完整性记录
    不创建普通 auto 备份
    不刷新 integrity.json
```

---

## 当前防护机制

### 1. 防丢失

程序启动时会自动备份数据库。

备份文件示例：

```text
%LOCALAPPDATA%\CheckMate\data_backups\auto_checkmate_20260504_200454.db
```

如果 `checkmate.db` 被误删、损坏或覆盖，可以从自动备份中恢复。

---

### 2. 防篡改检测

程序会记录数据库的 SHA256。

如果数据库被外部工具修改，下次启动时会检测到 hash 不一致，并提示数据库可能被修改或损坏。

注意：

当前机制不是阻止别人修改数据库，而是发现数据库被改过。

---

### 3. 可疑数据库隔离

检测到异常时，会生成：

```text
%LOCALAPPDATA%\CheckMate\data_backups\suspicious_checkmate_xxx.db
```

这份文件用于保留现场，方便之后排查或恢复。

检测到异常时不会刷新 `integrity.json`，防止把被篡改后的数据库“洗白”。

---

### 4. 恢复保护

从备份恢复数据库前，会先把当前数据库备份为：

```text
%LOCALAPPDATA%\CheckMate\data_backups\before_restore_checkmate_xxx.db
```

这样即使恢复错了，也还有机会找回恢复前的数据。

---

## 正常启动流程

推荐启动顺序：

```text
迁移旧数据库
↓
初始化数据库
↓
运行数据安全检查
↓
初始化主窗口 UI
↓
加载任务
↓
启动托盘、宠物和提醒管理器
```

对应代码示例：

```python
migration_result = migrate_legacy_database_if_needed()
print("数据库迁移检查：", migration_result["message"])

database.init_db()

self.data_guard_result = run_startup_data_guard()
```

---

## 数据迁移流程

```text
程序启动
↓
检查 AppData 中是否已有正式数据库
↓
如果正式数据库已存在：
    不覆盖，直接使用正式数据库

如果正式数据库不存在：
    检查项目目录下是否存在旧数据库

如果旧数据库存在：
    复制旧数据库到 AppData

如果旧数据库不存在：
    创建新的空数据库
```

迁移过程不会删除旧数据库。

旧目录可以暂时保留：

```text
CheckMate/data/
CheckMate/data_backups/
```

确认新版本稳定后，可以再手动清理旧目录。

---

## 检测到篡改时的流程

```text
启动程序
↓
发现 checkmate.db hash 不一致
↓
打印完整性警告
↓
生成 suspicious 可疑备份
↓
锁定完整性记录
↓
不创建普通 auto 备份
↓
不刷新 integrity.json
```

这样做是为了避免：

```text
数据库被外部篡改
↓
程序发现异常
↓
又把篡改后的数据库 hash 写入 integrity.json
↓
下次启动不再报警
```

也就是防止可疑数据库被“洗白”。

---

## 从最近自动备份恢复

可以通过底层函数从最近一次自动备份恢复数据库。

```python
from data_guard.backup_manager import restore_from_latest_auto_backup
from data_guard.integrity_manager import trust_current_database

result = restore_from_latest_auto_backup()

if result["success"]:
    trust_current_database()
```

恢复流程：

```text
找到最近的 auto 备份
↓
恢复前备份当前数据库
↓
用 auto 备份覆盖 checkmate.db
↓
信任恢复后的数据库
↓
刷新 integrity.json
```

---

## 正常数据库写入后的完整性刷新

程序内部正常修改数据库后，需要刷新完整性记录。

例如：

- 添加任务
- 编辑任务
- 删除任务
- 完成打卡
- 暂停 / 启用任务
- 更新宠物状态
- 保存宠物状态

推荐在 `database.py` 中统一封装：

```python
def refresh_integrity_after_db_change():
    try:
        refresh_integrity_record()
    except Exception as e:
        print("刷新数据库完整性记录失败：", e)
```

然后在数据库写入函数 `commit()` 和 `close()` 后调用。

如果当前数据库已经被判定为可疑状态，`refresh_integrity_record()` 会因为锁定机制而跳过刷新。

---

## 测试脚本

建议保留以下测试脚本：

```text
test/
├── test_tamper_db.py
└── test_restore_latest_backup.py
```

---

### `test_tamper_db.py`

用于模拟外部篡改数据库。

测试流程：

```text
1. 正常启动 CheckMate
2. 彻底退出 CheckMate
3. 运行 test_tamper_db.py
4. 再次启动 CheckMate
5. 应触发完整性警告
6. 应生成 suspicious 备份
```

测试脚本应使用正式数据库路径：

```python
from data_guard.paths import get_database_path

DB_PATH = get_database_path()
```

---

### `test_restore_latest_backup.py`

用于测试从最近自动备份恢复数据库。

测试流程：

```text
1. 确保已经存在 auto 备份
2. 运行 test_tamper_db.py 篡改数据库
3. 启动 CheckMate，确认报警
4. 彻底退出 CheckMate
5. 运行 test_restore_latest_backup.py
6. 再次启动 CheckMate
7. 应不再报警
```

---

## 当前限制

当前机制可以做到：

- 自动备份数据库
- 检测数据库是否被外部修改
- 保留可疑数据库副本
- 从最近自动备份恢复
- 防止可疑数据库被自动登记为正常数据
- 将用户数据与程序目录分离，降低更新程序时误删数据的风险

但不能做到：

- 绝对禁止用户修改数据库
- 防止高级逆向
- 防止用户同时修改数据库和 `integrity.json`
- 加密数据库内容
- 云端同步备份

对于本地 SQLite 桌面应用来说，当前目标是：

```text
普通用户不容易误删
程序更新不容易丢数据
数据被外部改过能发现
出问题后能从备份恢复
```

---

## 后续计划

后续可以在设置页面中加入“数据管理”区域，提供：

- 打开数据文件夹
- 打开备份文件夹
- 手动备份
- 从备份恢复
- 信任当前数据库
- 数据异常时弹窗提醒

可选增强：

- HMAC 校验
- 数据库加密
- 导出 / 导入用户数据
- 定期清理 suspicious 和 before_restore 备份
- 更正式的日志系统