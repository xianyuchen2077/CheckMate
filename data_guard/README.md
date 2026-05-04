# data_guard

`data_guard` 是 CheckMate 的数据安全模块，主要用于保护本地数据库，降低数据丢失和被外部篡改的风险。

当前模块的目标不是实现绝对安全，而是做到：

- 数据不容易因为误删、覆盖、更新而丢失
- 数据库被外部修改后能够被检测出来
- 检测到异常时不会把可疑数据库误认为正常数据库
- 出问题后可以从备份中恢复数据

---

## 目录结构

```text
data_guard/
├── __init__.py
├── paths.py
├── backup_manager.py
├── integrity_manager.py
├── startup_guard.py
└── README.md
```

项目运行后会生成：

```text
data/
└── checkmate.db

data_backups/
├── auto_checkmate_xxx.db
├── suspicious_checkmate_xxx.db
├── before_restore_checkmate_xxx.db
└── integrity.json
```

---

## 文件说明

### `paths.py`

统一管理数据安全相关路径。

主要负责：

- 获取数据库路径
- 获取备份目录
- 获取完整性校验文件路径
- 创建必要的数据目录

当前数据库路径：

```text
data/checkmate.db
```

当前备份目录：

```text
data_backups/
```

---

### `backup_manager.py`

负责数据库备份与恢复。

当前支持：

- 启动时自动备份数据库
- 创建可疑数据库备份
- 恢复前自动保护当前数据库
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

---

### `startup_guard.py`

负责程序启动时的数据安全检查流程。

主函数：

```python
run_startup_data_guard()
```

推荐在 `main_window.py` 中这样使用：

```python
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
data_backups/auto_checkmate_20260504_200454.db
```

如果 `checkmate.db` 被误删、损坏或覆盖，可以从自动备份中恢复。

---

### 2. 防篡改检测

程序会记录数据库的 SHA256。

如果数据库被外部工具修改，下次启动时会检测到 hash 不一致，并提示数据库可能被修改或损坏。

---

### 3. 可疑数据库隔离

检测到异常时，会生成：

```text
data_backups/suspicious_checkmate_xxx.db
```

这份文件用于保留现场，方便之后排查或恢复。

检测到异常时不会刷新 `integrity.json`，防止把被篡改后的数据库“洗白”。

---

### 4. 恢复保护

从备份恢复数据库前，会先把当前数据库备份为：

```text
data_backups/before_restore_checkmate_xxx.db
```

这样即使恢复错了，也还有机会找回恢复前的数据。

---

## 常用流程

### 正常启动

```text
database.init_db()
↓
run_startup_data_guard()
↓
检查完整性
↓
自动备份
↓
刷新 integrity.json
```

---

### 检测到篡改

```text
启动程序
↓
发现 checkmate.db hash 不一致
↓
打印警告
↓
生成 suspicious 备份
↓
锁定完整性记录
↓
不刷新 integrity.json
```

---

### 从最近自动备份恢复

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

## 测试脚本

建议保留以下测试脚本：

```text
test/
├── test_tamper_db.py
└── test_restore_latest_backup.py
```

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
- 数据库迁移到 AppData/Local/CheckMate
- 数据库加密
- 导出 / 导入用户数据
- 定期清理 suspicious 和 before_restore 备份