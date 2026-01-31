# JARVIS User Manual

Welcome to the JARVIS AI Agent User Manual. This directory contains comprehensive guides for using and managing your JARVIS system.

## 📁 Directory Structure

```
user_manual/
├── README.md                    # This file - main index
├── architecture/                # System architecture & design
│   └── system_architecture.md   # Complete system design guide
├── development/                 # Development & extension guides
│   ├── directory_structure.md   # Complete codebase reference
│   └── development_guide.md     # Building & extending JARVIS
├── monitoring/                  # Monitoring & observability guides
│   ├── monitoring_guide.md      # Complete monitoring system guide
│   └── metrics_reference.md     # Metrics and alerts reference
├── configuration/               # Configuration management guides
│   └── config_guide.md          # Configuration system guide
├── workflows/                   # Workflow management guides (future)
└── troubleshooting/            # Problem solving guides
    └── common_issues.md         # Common problems and solutions
```

## 🚀 Quick Start Guides

### Understanding JARVIS
- **System Architecture**: [architecture/system_architecture.md](architecture/system_architecture.md)
- **Directory Structure**: [development/directory_structure.md](development/directory_structure.md)

### Using JARVIS
- **Monitoring Dashboard**: [monitoring/monitoring_guide.md](monitoring/monitoring_guide.md)
- **Configuration Management**: [configuration/config_guide.md](configuration/config_guide.md)

### Developing JARVIS
- **Development Guide**: [development/development_guide.md](development/development_guide.md)
- **Code Reference**: [development/directory_structure.md](development/directory_structure.md)
- **Testing History**: [development/testing_history.md](development/testing_history.md)

### Troubleshooting
- **Common Issues**: [troubleshooting/common_issues.md](troubleshooting/common_issues.md)

## 🎯 Key Information

### Access Points
- **Grafana Dashboard**: http://localhost:3000 (admin/jarvis123)
- **Prometheus**: http://localhost:9091
- **Temporal UI**: http://localhost:8080
- **JARVIS Metrics**: http://localhost:9090/metrics

### CLI Tools
```bash
python config_cli.py show          # View configuration
python temporal_cli.py status      # Check workflows
python -c "from core.monitoring.metrics import jarvis_metrics; jarvis_metrics.start_metrics_server()"
```

### Development Commands
```bash
# Start monitoring
docker-compose -f docker-compose-monitoring.yml up -d

# Start Temporal
docker-compose -f docker-compose-temporal.yml up -d

# Test system
python config_cli.py test
```

## 📞 Support

For additional help:
1. Check the troubleshooting guides
2. Review system logs via monitoring dashboard
3. Use the configuration CLI tools for system status

---
*Last updated: January 31, 2026*
