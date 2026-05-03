# Push to GitHub｜上传到你的 GitHub 仓库

你的仓库地址：

```bash
https://github.com/davidwuw0811-boop/ai-stock-workbench
```

## 方法一：命令行上传

在本项目根目录执行：

```bash
git init
git add .
git commit -m "Initial commit: AI stock workbench MVP"
git branch -M main
git remote add origin https://github.com/davidwuw0811-boop/ai-stock-workbench.git
git push -u origin main
```

如果远程仓库已经有 README 或其他文件，先执行：

```bash
git pull origin main --allow-unrelated-histories
```

解决冲突后再 push。

## 方法二：GitHub 网页上传

1. 解压 zip
2. 打开仓库页面
3. 点击 `Add file` → `Upload files`
4. 将所有文件拖入
5. Commit changes

## 本地验证

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

打开：

```text
http://localhost:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开：

```text
http://localhost:3000
```
