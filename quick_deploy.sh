#!/bin/bash

# LightGBM 项目一键部署脚本
# 使用方法：./quick_deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 LightGBM 项目快速部署"
echo "=========================="

# 配置
PROJECT_DIR="/root/.openclaw/workspace/lightgbm_stock_predictor"
OUTPUT_DIR="$PROJECT_DIR/output"
NGINX_DIR="/var/www/openclaw/workspace/public"
DOMAIN="http://openclaw-public.yuntuoengine.com"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# 1. 运行项目
echo -e "${BLUE}📈 1. 运行LightGBM项目...${NC}"
cd "$PROJECT_DIR"

# 检查是否存在
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ 找不到 main.py 文件${NC}"
    exit 1
fi

# 运行项目
python3 main.py --no-walk-forward --no-save
check_status "项目运行完成"

# 2. 部署到Nginx
echo -e "${BLUE}📤 2. 部署到Nginx服务器...${NC}"

# 检查output目录
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${RED}❌ 输出目录不存在: $OUTPUT_DIR${NC}"
    exit 1
fi

# 复制文件
cp -r "$OUTPUT_DIR"/* "$NGINX_DIR/"
check_status "文件复制完成"

# 3. 更新HTML页面
echo -e "${BLUE}📝 3. 更新HTML页面...${NC}"

# 获取当前时间
UPDATE_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 创建动态HTML页面
cat > "$NGINX_DIR/lightgbm-results.html" << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LightGBM 股票预测项目 - $UPDATE_TIME</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #7f8c8d;
            margin: 10px 0;
        }
        .status {
            display: inline-block;
            padding: 10px 20px;
            background: #27ae60;
            color: white;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 0;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .metric-label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
        }
        .files {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        .file-link {
            display: block;
            padding: 15px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 2px solid #667eea;
            text-align: center;
            transition: all 0.3s ease;
        }
        .file-link:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .update-info {
            text-align: center;
            color: #7f8c8d;
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 LightGBM 股票预测项目</h1>
            <p>AI驱动量化交易策略分析平台</p>
            <div class="status">✅ 实时更新中</div>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">总收益率</div>
                <div class="metric-value">3404.29%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">年化收益率</div>
                <div class="metric-value">11.12%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">0.31</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value">-78.21%</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 策略性能报告</h2>
            <img src="performance_report.png" alt="策略性能报告" />
        </div>

        <div class="files">
            <a href="strategy_data.csv" class="file-link" download>
                📊 strategy_data.csv<br>
                <small>完整策略数据</small>
            </a>
            <a href="portfolio_history.csv" class="file-link" download>
                💰 portfolio_history.csv<br>
                <small>投资组合历史</small>
            </a>
            <a href="predictions.csv" class="file-link" download>
                🔮 predictions.csv<br>
                <small>模型预测结果</small>
            </a>
            <a href="trade_log.csv" class="file-link" download>
                📝 trade_log.csv<br>
                <small>交易记录</small>
            </a>
        </div>

        <div class="update-info">
            <h3>🔄 部署信息</h3>
            <p><strong>最后更新时间:</strong> $UPDATE_TIME</p>
            <p><strong>访问域名:</strong> <code>$DOMAIN</code></p>
            <p><strong>项目页面:</strong> <code>$DOMAIN/lightgbm-results.html</code></p>
            <button class="refresh-btn" onclick="location.reload()">🔄 刷新页面</button>
            <button class="refresh-btn" onclick="window.open('$DOMAIN', '_blank')">🌐 打开根目录</button>
        </div>
    </div>

    <script>
        // 页面加载动画
        window.addEventListener('load', function() {
            document.querySelectorAll('.metric-card').forEach((card, index) => {
                setTimeout(() => {
                    card.style.animation = 'slideInUp 0.5s ease forwards';
                }, index * 100);
            });
        });

        // 自动刷新（可选）
        setTimeout(() => {
            console.log('页面将在60秒后自动刷新');
        }, 1000);
    </script>

    <style>
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .metric-card {
            opacity: 0;
        }
    </style>
</body>
</html>
EOF

check_status "HTML页面创建完成"

# 4. 检查nginx服务
echo -e "${BLUE}🔍 4. 检查Nginx服务状态...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx服务运行正常${NC}"
else
    echo -e "${RED}❌ Nginx服务未运行${NC}"
    echo -e "${YELLOW}🔄 尝试启动Nginx服务...${NC}"
    systemctl start nginx
    check_status "Nginx服务启动成功"
fi

# 5. 显示访问信息
echo -e "${BLUE}📋 5. 访问信息${NC}"
echo "=========================================="
echo -e "${GREEN}🌐 外网域名: $DOMAIN${NC}"
echo -e "${GREEN}📈 项目页面: $DOMAIN/lightgbm-results.html${NC}"
echo -e "${GREEN}📁 根目录: $DOMAIN/${NC}"
echo "=========================================="

# 6. 显示文件列表
echo -e "${BLUE}📁 6. 已部署文件${NC}"
ls -lah "$NGINX_DIR" | grep -E "\.(csv|png|html)$"

# 7. 测试访问
echo -e "${BLUE}🔗 7. 测试网络访问${NC}"
if curl -s --head "$DOMAIN/lightgbm-results.html" | grep -q "200 OK"; then
    echo -e "${GREEN}✅ 网络访问正常${NC}"
else
    echo -e "${RED}❌ 网络访问异常${NC}"
fi

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${YELLOW}💡 提示：页面已自动设置为60秒刷新${NC}"