#!/bin/bash
# 答案之书 · 播客版 — ECS 部署脚本
# 用法: bash deploy.sh

set -e
REPO="https://github.com/zzstart2/podcast-knowledge-base.git"
APP_DIR="/opt/podcast-lib"
SERVICE="podcast-lib"

echo "=== 答案之书 部署脚本 ==="

# 1. 依赖
echo "[1/5] 安装系统依赖..."
apt-get update -q && apt-get install -y python3 python3-pip git nginx

# 2. 拉代码
if [ -d "$APP_DIR/.git" ]; then
    echo "[2/5] 更新代码..."
    git -C "$APP_DIR" pull
else
    echo "[2/5] 克隆代码..."
    git clone "$REPO" "$APP_DIR"
fi

# 3. Python 依赖
echo "[3/5] 安装 Python 依赖..."
pip3 install -r "$APP_DIR/requirements.txt" -q

# 4. 配置环境变量
if [ ! -f "$APP_DIR/.env" ]; then
    echo "[4/5] 创建 .env 文件..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "⚠  请编辑 $APP_DIR/.env，填入 MINIMAX_API_KEY"
    echo "   vim $APP_DIR/.env"
    echo ""
    read -p "填好了按回车继续..." _
else
    echo "[4/5] .env 已存在，跳过"
fi

# 5. 重建数据库（从 enriched JSON）
echo "[5/5] 重建数据库..."
cd "$APP_DIR"
python3 tools/import_db.py --input data/enriched/*.json
python3 tools/embed.py
echo "✔ 数据库就绪"

# 6. 创建 systemd service
cat > /etc/systemd/system/$SERVICE.service << UNIT
[Unit]
Description=答案之书 播客版
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=/usr/bin/python3 tools/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE
echo "✔ 服务已启动: systemctl status $SERVICE"

# 7. Nginx 配置（追加到现有 nginx，不覆盖）
NGINX_CONF="/etc/nginx/sites-available/podcast-lib"
if [ ! -f "$NGINX_CONF" ]; then
    cat > "$NGINX_CONF" << NGINX
server {
    listen 80;
    server_name _;          # 改为你的域名或 IP

    location /podcast/ {
        proxy_pass         http://127.0.0.1:3000/;
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
    }
}
NGINX
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/podcast-lib
    nginx -t && nginx -s reload
    echo "✔ Nginx 配置完成，访问 http://<你的IP>/podcast/"
else
    echo "✔ Nginx 配置已存在，如需修改：vim $NGINX_CONF"
fi

echo ""
echo "=== 部署完成 ==="
echo "  服务状态: systemctl status $SERVICE"
echo "  查看日志: journalctl -u $SERVICE -f"
echo "  更新应用: git -C $APP_DIR pull && systemctl restart $SERVICE"
