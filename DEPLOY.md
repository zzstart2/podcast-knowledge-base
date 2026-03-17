# 🚀 GitHub Pages 部署指南

## 快速部署步骤

### 1. 上传到GitHub

1. 在GitHub上创建新仓库 `podcast-qa-system`
2. 将本地代码推送到GitHub：

```bash
git remote add origin https://github.com/你的用户名/podcast-qa-system.git
git push -u origin master
```

### 2. 启用GitHub Pages

1. 进入你的GitHub仓库
2. 点击 Settings（设置）
3. 滚动到 Pages 部分
4. 在 Source 中选择 "Deploy from a branch"
5. 选择 branch: `master` 和 folder: `/ (root)`
6. 点击 Save（保存）

### 3. 访问你的应用

几分钟后，你的播客解答器将在以下地址可用：
```
https://你的用户名.github.io/podcast-qa-system/
```

## 🎯 功能验证

部署成功后，可以测试以下功能：

- ✅ 输入问题："如何提高工作效率？"
- ✅ 点击热门问题标签
- ✅ 查看推荐结果和播客链接
- ✅ 响应式设计在手机上的表现

## 📝 自定义配置

### 修改GitHub链接
编辑 `index.html`，找到以下行并替换为你的GitHub用户名：
```html
<a href="https://github.com/你的用户名/podcast-qa-system" target="_blank">
```

### 添加自定义域名（可选）
1. 在仓库根目录创建 `CNAME` 文件
2. 写入你的域名，如：`podcast.yourdomain.com`
3. 在域名DNS设置中添加CNAME记录指向 `你的用户名.github.io`

## 🔧 本地开发

如果需要本地开发和测试：

```bash
# 克隆项目
git clone https://github.com/你的用户名/podcast-qa-system.git
cd podcast-qa-system

# 直接用浏览器打开 index.html
# 或者使用简单的HTTP服务器
python -m http.server 8000
```

## 🚀 进阶部署

### Vercel部署（推荐）
1. 访问 [vercel.com](https://vercel.com)
2. 连接GitHub账号
3. 导入 `podcast-qa-system` 仓库
4. 自动部署，获得自定义域名

### Netlify部署
1. 访问 [netlify.com](https://netlify.com)  
2. 连接GitHub仓库
3. 设置构建命令（留空）
4. 设置发布目录：`/`（根目录）
5. 点击部署

## 📊 性能优化建议

- 启用CDN加速
- 配置GZIP压缩
- 添加缓存策略
- 监控访问统计

## 🐛 常见问题

**Q: 页面显示404错误？**
A: 检查GitHub Pages设置，确保选择了正确的分支和目录。

**Q: 样式没有加载？**
A: 确保所有资源使用相对路径，避免本地绝对路径。

**Q: 搜索功能不工作？**
A: 这是纯前端应用，搜索基于本地JavaScript，应该正常工作。检查浏览器控制台是否有错误。

---

🎉 恭喜！你的播客解答器现在可以通过外网访问了！