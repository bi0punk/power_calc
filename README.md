# Electrico v2 — Simulador Solar & Baterías

Aplicación Flask con interfaz técnica oscura para modelar sistemas fotovoltaicos off-grid / híbridos. Calcula energía nominal, consumo, generación solar, balance energético y autonomía.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![CI](https://github.com/bi0punk/power_calc/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/power_calc/actions/workflows/ci.yml)

## Tabla de Contenidos

- [Características](#características)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Tests](#tests)
- [Configuración](#configuración)
- [CI](#ci)
- [Fórmulas](#fórmulas)
- [Limitaciones / Roadmap](#limitaciones--roadmap)
- [Licencia](#licencia)

## Características

- Cálculo de energía nominal y útil (AC) del banco de baterías
- Consumo instantáneo y diario por carga/equipo
- Generación solar útil diaria estimada (HSP × eficiencias)
- Balance energético diario solar vs. consumo
- Autonomía: solo batería, por perfil diario, híbrida solar+batería
- Interfaz dark técnica con Chart.js, badges de estado y diseño responsivo

## Stack

- Python 3.10+, Flask 3.1, Chart.js, Bootstrap, JetBrains Mono

## Arquitectura

```
power_calc/
├── app.py                 # Lógica de cálculo + rutas Flask
├── templates/
│   └── index.html         # Interfaz de usuario
├── static/
│   ├── css/
│   └── js/
├── data/                  # Datos de ejemplo
├── tests/
├── requirements.txt
├── pyproject.toml
├── run.sh
├── .env.example
└── README.md
```

## Requisitos

- Python 3.10+

## Instalación

```bash
git clone https://github.com/bi0punk/power_calc.git
cd power_calc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

Abrir `http://127.0.0.1:5000`. Ingresar datos de baterías, consumos y paneles solares, y presionar "Calcular" para ver los resultados.

```bash
# O usando run.sh
bash run.sh
```

## Tests

```bash
pip install pytest ruff
pytest -q
ruff check .
```

## Configuración

Variables de entorno (ver `.env.example`):

| Variable     | Default          | Descripción                     |
|--------------|------------------|---------------------------------|
| `SECRET_KEY` | (auto-generada)  | Clave secreta Flask             |
| `DEBUG`      | `false`          | Modo debug                      |

## CI

GitHub Actions ejecuta ruff lint + pytest en cada push y PR.

## Fórmulas

- `Wh_banco = Voltaje × Ah × Cantidad`
- `SOC_min = 100 − DOD`
- `fraccion_SOC = max(0, SOC_inicial − SOC_min) / 100`
- `Wh_util_AC = Wh_banco × fraccion_SOC × η_descarga × η_inversor`
- `Wh_solar_dia = W_paneles × HSP × η_solar × η_inversor`
- `Autonomia_h = Wh_util_AC / W_carga_total`
- `Autonomia_hibrida_dias = Wh_util_AC / |deficit_diario|`

## Limitaciones / Roadmap

- [ ] Soporte para múltiples bancos de baterías con diferentes químicas
- [ ] Curvas de descarga personalizadas (Peukert)
- [ ] Simulación horaria con perfil de carga variable
- [ ] Exportación de resultados a PDF
- [ ] Almacenamiento de configuraciones (presets)

## Licencia

MIT
