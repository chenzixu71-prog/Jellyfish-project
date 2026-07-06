# 微信开发者工具导入说明

当前正式前端是 Taro 4.x 工程，请导入 `frontend` 目录，不要导入旧的 `miniprogram` 目录。

## 正确导入目录

```text
C:\Users\陈梓旭\OneDrive\桌面\workspace\tmp\Jellyfish-project-push\02-Python全栈AI刷题学习小程序\frontend
```

`frontend/project.config.json` 已配置：

```json
{
  "miniprogramRoot": "./dist"
}
```

所以微信开发者工具导入 `frontend` 后，会自动使用 `frontend/dist` 里的最新构建产物。

## 不要导入

```text
C:\Users\陈梓旭\OneDrive\桌面\workspace\tmp\Jellyfish-project-push\02-Python全栈AI刷题学习小程序\miniprogram
```

这个目录只是早期原生小程序骨架，里面是旧 UI。

## 如果仍然显示旧 UI

1. 在微信开发者工具里关闭当前项目。
2. 重新打开微信开发者工具，选择“导入项目”。
3. 项目目录选择 `frontend`，不是 `miniprogram`。
4. 导入后点击：

```text
工具 -> 清缓存 -> 清除全部缓存
```

5. 再点击：

```text
编译
```

## 新 UI 验证点

正确导入后，首页应该能看到：

- `Jelly Quest`
- `水母 DIY 学习助手`
- 蓝色水母插画
- `让水母生成题目` 按钮

