# Electrico v2 — Simulador Solar & Baterías

Aplicación Flask con interfaz técnica oscura para modelar sistemas fotovoltaicos off-grid / híbridos.

## Qué calcula

- Energía nominal y útil (AC) del banco de baterías
- Consumo instantáneo y diario por carga
- Generación solar útil diaria estimada (HSP × eficiencias)
- Balance energético diario solar vs. consumo
- Autonomía: solo batería, por perfil diario, híbrida solar+batería
- Análisis individual por equipo

## Novedades v2

- Interfaz dark técnica (tema oscuro con acentos cyan/verde)
- Tipografía monoespaciada JetBrains Mono para métricas
- 4 tarjetas de métricas principales con indicador de color
- Gráfico de barras apiladas (Chart.js) consumo solar vs. batería por equipo
- Barra visual de estado SOC (utilizable / mínimo)
- Badges de estado del sistema (Sostenible / Déficit / Sin consumo)
- Diseño responsivo con sidebar sticky en desktop
- Spinner animado en botón Calcular durante submit

## Requisitos

- Python 3.10+
- Flask 3.1.0

## Instalación y uso

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir: http://127.0.0.1:5000

## Fórmulas principales

- `Wh_banco = Voltaje × Ah × Cantidad`
- `SOC_min = 100 − DOD`
- `fraccion_SOC = max(0, SOC_inicial − SOC_min) / 100`
- `Wh_util_AC = Wh_banco × fraccion_SOC × η_descarga × η_inversor`
- `Wh_solar_dia = W_paneles × HSP × η_solar × η_inversor`
- `Autonomia_h = Wh_util_AC / W_carga_total`
- `Autonomia_hibrida_dias = Wh_util_AC / |deficit_diario|`

## Nota técnica

Modelo de estimación preliminar. La autonomía real puede ser menor por:
temperatura de batería, envejecimiento, corrientes de descarga altas,
pérdidas en cableado, y comportamiento cíclico de compresores/motores.
