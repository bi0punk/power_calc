# Simulador de baterías, cargas y paneles solares

Aplicación Flask + Bootstrap lista para correr en Linux. Permite modelar:

- Banco de baterías por voltaje, Ah y cantidad
- Cargas / electrodomésticos por potencia, horas de uso y cantidad
- Paneles solares por potencia y cantidad
- Parámetros técnicos del sistema

## Qué calcula

1. Energía nominal total del banco de baterías (Wh)
2. Energía útil en AC considerando:
   - profundidad máxima de descarga
   - estado de carga inicial
   - eficiencia de descarga de batería
   - eficiencia del inversor
3. Potencia instantánea total de la carga (W)
4. Consumo diario total (Wh/día)
5. Generación solar útil diaria estimada (Wh/día)
6. Balance energético diario
7. Autonomía:
   - solo batería
   - batería + solar
   - por electrodoméstico individual

## Fórmulas principales

- `Wh_batería = Voltaje × Ah × Cantidad`
- `SOC_mínimo = 100 - DOD`
- `fracción_SOC_utilizable = max(0, SOC_inicial - SOC_mínimo) / 100`
- `Wh_útiles_AC = Wh_nominal × fracción_SOC_utilizable × eficiencia_descarga × eficiencia_inversor`
- `Wh_día_carga = Potencia × horas_día × cantidad`
- `Wh_solar_día = W_paneles × HSP × eficiencia_solar × eficiencia_inversor`
- `autonomía_horas = Wh_útiles_AC / W_carga_total`
- `autonomía_híbrida_días = Wh_útiles_AC / déficit_diario`

## Requisitos

- Linux
- Python 3.10+

## Ejecución rápida

```bash
cd battery_sim_app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Luego abre:

```bash
http://127.0.0.1:5000
```

## Ejecución con script

```bash
cd battery_sim_app
./run.sh
```

## Notas técnicas

- Es una estimación de ingeniería de primer nivel, no reemplaza ensayo real.
- La autonomía real puede bajar por temperatura, envejecimiento de batería, corrientes altas, pérdidas en cableado y comportamiento cíclico del equipo.
- Para refrigeradores, bombas y motores, conviene modelar también el pico de arranque del inversor en una siguiente versión.

## Próximas mejoras sugeridas

- Persistencia en SQLite
- Historial de simulaciones
- Exportación PDF/CSV
- Cálculo de corriente por rama DC/AC
- Verificación de dimensionamiento del inversor y controlador MPPT/PWM
- Perfil horario real por tramos día/noche
