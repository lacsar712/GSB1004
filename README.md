# 体检信息管理系统

一个功能完整、架构合理的基于Web的体检信息管理系统，采用Flask + SQLite + Bootstrap 5技术栈开发，支持Docker一键部署。

## ✨ 功能特性

- 🔐 **用户认证系统**：支持管理员、医护人员、普通用户三种角色，完整的权限控制
- 📅 **体检预约管理**：选择体检套餐、预约日期和时间，自动冲突检测
- 📝 **体检数据录入**：医护人员录入各项体检指标数据，支持数据验证
- 📊 **体检报告查看**：个人体检报告查看，支持 Chart.js 数据可视化
- 🎨 **现代化 UI**：使用 Bootstrap 5，卡片化布局、流畅交互、响应式设计
- 🐳 **完全容器化**：Docker Compose 一键启动，无需本地环境依赖

## 🛠 技术栈

- **前端**: HTML + Bootstrap 5 + JavaScript + Chart.js
- **后端**: Python Flask 3.0 + Flask-SQLAlchemy + Flask-Login
- **数据库**: SQLite（开发环境）
- **服务器**: Gunicorn (WSGI) + Nginx (反向代理)
- **部署**: Docker + Docker Compose

## 📦 项目结构

```
health/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── models.py                # 数据模型
│   ├── extensions.py            # Flask 扩展
│   ├── access.py                # 权限装饰器
│   ├── auth/                    # 认证模块
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── appointments/            # 预约模块
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── records/                 # 数据录入模块
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── reports/                 # 报告模块
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/                    # 主页模块
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   │   └── styles.css       # 自定义样式
│   │   └── js/
│   │       └── toast.js         # Toast 通知组件
│   │   └── vendor/
│   │       └── chartjs/
│   │           └── chart.umd.min.js  # 本地图表库
│   └── templates/               # Jinja2 模板
│       ├── base.html            # 基础模板
│       ├── auth/                # 认证页面
│       ├── appointments/        # 预约页面
│       ├── records/             # 数据录入页面
│       ├── reports/             # 报告页面
│       └── main/                # 主页
├── instance/                    # 实例文件夹（数据库）
├── logs/                        # 日志目录
├── config.py                    # 配置文件
├── run.py                       # 应用入口
├── requirements.txt             # Python 依赖
├── Dockerfile                   # 后端容器配置
├── docker-compose.yml           # Docker Compose 配置
├── nginx.conf                   # Nginx 反向代理配置
├── .dockerignore                # Docker 忽略文件
├── .gitignore                   # Git 忽略文件
└── README.md                    # 项目文档
```

## 🚀 快速开始

### 前置要求

- Docker Desktop（已启动）
- 前端端口：4004
- 后端端口：9004
- 确保端口未被占用

### 启动步骤

1. **克隆项目**（或进入项目目录）

   ```bash
   cd /path/to/health
   ```

2. **一键启动**

   ```bash
   docker compose up --build
   ```

3. **等待容器启动**（约 2-3 分钟）

   启动完成后，您将看到类似以下日志：

   ```
   health_backend  | Booting worker with pid: 1
   health_frontend | /docker-entrypoint.sh: Configuration complete
   ```

4. **访问系统**

   - 前端地址: [http://localhost:4004](http://localhost:4004)

### 测试账号

系统初始化时会自动创建以下测试账号：

| 角色     | 用户名 | 密码   | 权限说明                         |
| -------- | ------ | ------ | -------------------------------- |
| 管理员   | admin  | 123456 | 所有权限，可查看全部数据         |
| 医护人员 | staff  | 123456 | 可录入体检数据、查看所有预约     |
| 普通用户 | user   | 123456 | 可创建和查看个人预约、查看个人报告 |
| 普通用户 | user2  | 123456 | 可创建和查看个人预约、查看个人报告 |

## 📋 核心功能演示

### 1. 用户登录

- 访问 http://localhost:4004
- 使用测试账号登录
- 系统自动识别角色并分配权限

### 2. 体检预约

- 普通用户登录后点击「新建预约」
- 选择体检套餐（基础/全面/高端）
- 选择预约日期和时间
- 提交后自动检测时间冲突

### 3. 数据录入

- 医护人员登录后进入「数据录入」
- 选择待录入的预约
- 填写各项体检指标（身高、体重、血压等）
- 提交后自动更新预约状态为「已完成」

### 4. 报告查看

- 用户登录后进入「体检报告」
- 选择已完成的预约查看报告
- 查看指标趋势图表和明细表格

## 🐳 Docker 配置说明

### 服务架构

本项目采用前后端分离架构，通过 Docker Compose 编排：

```yaml
services:
  backend:    # Flask 后端服务
    - 端口: 9004:5000
    - 镜像: Python 3.11
    - WSGI: Gunicorn
    
  frontend:   # Nginx 前端服务
    - 端口: 4004:80
    - 镜像: Nginx Alpine
    - 反向代理后端 API
```

### 数据持久化

- 数据库文件存储在 Docker Volume: `backend_data`
- 日志文件存储在 Docker Volume: `backend_logs`
- 即使重启容器，数据也不会丢失

### 常用命令

```bash
# 启动服务
docker compose up

# 后台启动
docker compose up -d

# 停止服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 查看日志
docker compose logs -f

# 查看后端日志
docker compose logs -f backend

# 重新构建并启动
docker compose up --build

# 进入后端容器
docker compose exec backend bash
```

## 🎨 UI/UX 设计亮点

遵循现代 Web 设计规范，提供极致的用户体验：

- **Bootstrap 组件化布局**：导航栏、表单、表格、卡片统一使用 Bootstrap 5 组件
- **卡片增强样式**：在 Bootstrap 基础上补充统一阴影与圆角风格
- **流畅交互**：表单校验、图表切换、筛选按钮均提供即时反馈
- **Toast 通知**：操作成功/失败时弹出自动消失的优雅提示
- **数据可视化**：Chart.js 柱状图展示体检指标趋势
- **响应式设计**：支持 PC、平板、手机多端适配

## 📚 数据模型

### 核心表结构

#### User (用户表)

- `id`: 主键
- `username`: 用户名（唯一）
- `password_hash`: 密码哈希
- `role`: 角色（admin/staff/user）
- `created_at`: 创建时间

#### Package (体检套餐表)

- `id`: 主键
- `name`: 套餐名称
- `description`: 套餐描述
- `price`: 价格（分）

#### Appointment (预约表)

- `id`: 主键
- `user_id`: 用户 ID（外键）
- `package_id`: 套餐 ID（外键）
- `scheduled_date`: 预约日期
- `scheduled_time`: 预约时间
- `status`: 状态（scheduled/completed）
- `created_at`: 创建时间

#### MetricDefinition (指标定义表)

- `id`: 主键
- `name`: 指标名称（如"身高"）
- `unit`: 单位（如"cm"）
- `normal_range`: 正常范围

#### MetricRecord (指标记录表)

- `id`: 主键
- `appointment_id`: 预约 ID（外键）
- `metric_definition_id`: 指标定义 ID（外键）
- `value`: 指标值
- `recorded_by_id`: 录入人 ID（外键）
- `recorded_at`: 录入时间

## 🔧 开发指南

### 本地开发（不使用 Docker）

1. **创建虚拟环境**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **运行开发服务器**

   ```bash
   python run.py
   ```

4. **访问应用**

   http://localhost:5000

### 添加新功能

1. 在对应模块的 `routes.py` 中添加路由
2. 在 `templates/` 中创建对应的 HTML 模板
3. 如需修改数据模型，编辑 `app/models.py`
4. 重启服务生效

## 🧪 测试

### 功能测试清单

- [ ] 登录功能（正确密码/错误密码）
- [ ] 角色权限（管理员/医护/用户）
- [ ] 预约创建（正常/时间冲突）
- [ ] 数据录入（完整填写/不完整）
- [ ] 报告查看（有数据/无数据）
- [ ] 权限控制（访问限制页面）

### 响应式测试

- [ ] PC 端 (1920x1080)
- [ ] 平板端 (768x1024)
- [ ] 手机端 (375x667)

## 📖 API 文档

### 认证接口

- `POST /auth/login` - 用户登录
- `GET /auth/logout` - 用户登出

### 预约接口

- `GET /appointments/` - 查看预约列表（admin/staff 查看全部，user 查看本人）
- `GET /appointments/new` - 新建预约表单（admin/staff/user）
- `POST /appointments/new` - 提交新预约（user 仅为自己预约；admin/staff 可为普通用户预约）

### 数据录入接口

- `GET /records/` - 查看待录入预约列表
- `GET /records/<id>` - 数据录入表单
- `POST /records/<id>` - 提交体检数据

### 报告接口

- `GET /reports/` - 查看报告列表
- `GET /reports/<id>` - 查看报告详情

## 🐛 常见问题

### Q: Docker 容器启动失败？

**A**: 检查以下内容：
- Docker Desktop 是否正常运行
- 端口 4004 和 5000 是否被占用
- 查看日志: `docker compose logs`

### Q: 数据库数据丢失？

**A**: 确保使用 `docker compose down` 而非 `docker compose down -v`。后者会删除数据卷。

### Q: 前端无法访问后端 API？

**A**: 检查 Nginx 配置中的 `proxy_pass` 是否正确指向 `backend:5000`。

### Q: CSS 样式不生效？

**A**: 
- 清除浏览器缓存（Ctrl + F5 / Cmd + Shift + R）
- 检查 Bootstrap 5 CDN 是否加载成功

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

体检信息管理系统开发团队

---

**最后更新**: 2026-03-04

**版本**: v1.0.0
