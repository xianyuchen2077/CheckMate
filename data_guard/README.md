# data_guard

`data_guard` 是 CheckMate 的数据安全模块。

当前阶段目标：

1. 防止数据库因为误删、覆盖、更新而丢失。
2. 程序启动时自动备份 `data/checkmate.db`。
3. 自动备份只保留最近 10 个，避免无限占用空间。
4. 后续增加手动备份、恢复备份、完整性校验、防篡改检测。

## 文件说明

### paths.py

统一管理数据路径。

当前数据库路径：

```text
data/checkmate.db