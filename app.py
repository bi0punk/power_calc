from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'battery-sim-local-dev'


@dataclass
class Battery:
    name: str
    voltage: float
    ah: float
    quantity: int

    @property
    def nominal_wh(self) -> float:
        return self.voltage * self.ah * self.quantity


@dataclass
class Appliance:
    name: str
    power_w: float
    hours_per_day: float
    quantity: int

    @property
    def instant_power_w(self) -> float:
        return self.power_w * self.quantity

    @property
    def daily_wh(self) -> float:
        return self.power_w * self.hours_per_day * self.quantity


@dataclass
class SolarPanel:
    name: str
    power_w: float
    quantity: int

    @property
    def total_power_w(self) -> float:
        return self.power_w * self.quantity


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip().replace(',', '.')
        return float(text) if text else default
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def parse_rows(prefix: str) -> List[Dict[str, str]]:
    names = request.form.getlist(f'{prefix}_name')
    fields = {
        key: request.form.getlist(f'{prefix}_{key}')
        for key in request.form.keys()
        if key.startswith(f'{prefix}_') and key != f'{prefix}_name'
    }

    rows: List[Dict[str, str]] = []
    for idx, name in enumerate(names):
        row = {'name': name}
        for full_key, values in fields.items():
            short_key = full_key.replace(f'{prefix}_', '', 1)
            row[short_key] = values[idx] if idx < len(values) else ''
        rows.append(row)
    return rows


def build_batteries() -> List[Battery]:
    items: List[Battery] = []
    for row in parse_rows('battery'):
        voltage = to_float(row.get('voltage'), 0.0)
        ah = to_float(row.get('ah'), 0.0)
        quantity = max(0, to_int(row.get('quantity'), 0))
        name = row.get('name', '').strip() or 'Batería'
        if voltage > 0 and ah > 0 and quantity > 0:
            items.append(Battery(name=name, voltage=voltage, ah=ah, quantity=quantity))
    return items


def build_appliances() -> List[Appliance]:
    items: List[Appliance] = []
    for row in parse_rows('appliance'):
        power_w = to_float(row.get('power_w'), 0.0)
        hours_per_day = to_float(row.get('hours_per_day'), 0.0)
        quantity = max(0, to_int(row.get('quantity'), 0))
        name = row.get('name', '').strip() or 'Equipo'
        if power_w > 0 and quantity > 0 and hours_per_day >= 0:
            items.append(
                Appliance(
                    name=name,
                    power_w=power_w,
                    hours_per_day=hours_per_day,
                    quantity=quantity,
                )
            )
    return items


def build_panels() -> List[SolarPanel]:
    items: List[SolarPanel] = []
    for row in parse_rows('panel'):
        power_w = to_float(row.get('power_w'), 0.0)
        quantity = max(0, to_int(row.get('quantity'), 0))
        name = row.get('name', '').strip() or 'Panel'
        if power_w > 0 and quantity > 0:
            items.append(SolarPanel(name=name, power_w=power_w, quantity=quantity))
    return items


def default_payload() -> Dict[str, Any]:
    return {
        'inputs': {
            'peak_sun_hours': 4.5,
            'solar_system_efficiency_pct': 80.0,
            'inverter_efficiency_pct': 90.0,
            'battery_discharge_efficiency_pct': 95.0,
            'max_depth_of_discharge_pct': 80.0,
            'initial_soc_pct': 100.0,
        },
        'batteries': [
            {'name': 'Batería AGM 12V', 'voltage': 12, 'ah': 100, 'quantity': 1},
        ],
        'appliances': [
            {'name': 'Refrigerador', 'power_w': 100, 'hours_per_day': 10, 'quantity': 1},
        ],
        'panels': [
            {'name': 'Panel solar', 'power_w': 450, 'quantity': 1},
        ],
    }


def extract_payload_from_request() -> Dict[str, Any]:
    return {
        'inputs': {
            'peak_sun_hours': to_float(request.form.get('peak_sun_hours'), 4.5),
            'solar_system_efficiency_pct': to_float(request.form.get('solar_system_efficiency_pct'), 80.0),
            'inverter_efficiency_pct': to_float(request.form.get('inverter_efficiency_pct'), 90.0),
            'battery_discharge_efficiency_pct': to_float(request.form.get('battery_discharge_efficiency_pct'), 95.0),
            'max_depth_of_discharge_pct': to_float(request.form.get('max_depth_of_discharge_pct'), 80.0),
            'initial_soc_pct': to_float(request.form.get('initial_soc_pct'), 100.0),
        },
        'batteries': [asdict(item) for item in build_batteries()],
        'appliances': [asdict(item) for item in build_appliances()],
        'panels': [asdict(item) for item in build_panels()],
    }


def format_duration_hours(hours: float) -> str:
    if hours <= 0:
        return '0 h'
    if hours >= 24:
        days = hours / 24.0
        return f'{hours:,.2f} h ({days:,.2f} días)'
    return f'{hours:,.2f} h'


def calculate(payload: Dict[str, Any]) -> Dict[str, Any]:
    batteries = [Battery(**row) for row in payload['batteries']]
    appliances = [Appliance(**row) for row in payload['appliances']]
    panels = [SolarPanel(**row) for row in payload['panels']]

    psh = max(0.0, to_float(payload['inputs'].get('peak_sun_hours'), 4.5))
    solar_eff = clamp(to_float(payload['inputs'].get('solar_system_efficiency_pct'), 80.0) / 100.0, 0.0, 1.0)
    inverter_eff = clamp(to_float(payload['inputs'].get('inverter_efficiency_pct'), 90.0) / 100.0, 0.0, 1.0)
    battery_eff = clamp(to_float(payload['inputs'].get('battery_discharge_efficiency_pct'), 95.0) / 100.0, 0.0, 1.0)
    dod_pct = clamp(to_float(payload['inputs'].get('max_depth_of_discharge_pct'), 80.0), 0.0, 100.0)
    initial_soc_pct = clamp(to_float(payload['inputs'].get('initial_soc_pct'), 100.0), 0.0, 100.0)

    min_soc_pct = max(0.0, 100.0 - dod_pct)
    accessible_soc_pct = max(0.0, initial_soc_pct - min_soc_pct)
    accessible_fraction = accessible_soc_pct / 100.0

    total_battery_nominal_wh = sum(item.nominal_wh for item in batteries)
    total_battery_ac_usable_wh = total_battery_nominal_wh * accessible_fraction * battery_eff * inverter_eff
    total_panel_power_w = sum(item.total_power_w for item in panels)
    solar_daily_useful_wh = total_panel_power_w * psh * solar_eff * inverter_eff
    total_load_power_w = sum(item.instant_power_w for item in appliances)
    total_load_daily_wh = sum(item.daily_wh for item in appliances)

    battery_only_hours = (total_battery_ac_usable_wh / total_load_power_w) if total_load_power_w > 0 else None
    battery_only_days_by_profile = (total_battery_ac_usable_wh / total_load_daily_wh) if total_load_daily_wh > 0 else None

    daily_balance_wh = solar_daily_useful_wh - total_load_daily_wh
    if total_load_daily_wh <= 0:
        solar_status = 'Sin consumo diario configurado.'
        hybrid_days = None
    elif daily_balance_wh >= 0:
        solar_status = 'Sistema sostenible en promedio diario. La generación solar cubre o supera el consumo diario.'
        hybrid_days = None
    else:
        solar_status = 'Sistema no sostenible en promedio diario. La batería cubrirá el déficit hasta agotarse.'
        hybrid_days = total_battery_ac_usable_wh / abs(daily_balance_wh) if abs(daily_balance_wh) > 0 else None

    appliance_rows = []
    for appliance in appliances:
        single_power = appliance.instant_power_w
        single_daily = appliance.daily_wh
        battery_hours = (total_battery_ac_usable_wh / single_power) if single_power > 0 else None
        if single_daily > 0:
            if solar_daily_useful_wh >= single_daily:
                solar_runtime = 'Sostenible en promedio diario'
            else:
                solar_runtime = format_duration_hours(total_battery_ac_usable_wh / max(single_daily - solar_daily_useful_wh, 1e-9) * 24)
        else:
            solar_runtime = 'Sin horas/día definidas'

        appliance_rows.append(
            {
                'name': appliance.name,
                'quantity': appliance.quantity,
                'power_w': appliance.power_w,
                'instant_power_w': single_power,
                'hours_per_day': appliance.hours_per_day,
                'daily_wh': single_daily,
                'battery_only_hours': battery_hours,
                'solar_runtime': solar_runtime,
            }
        )

    warnings: List[str] = []
    if not batteries:
        warnings.append('No agregaste baterías válidas. Sin batería no existe autonomía acumulada.')
    if not appliances:
        warnings.append('No agregaste consumos válidos. Debes definir al menos un electrodoméstico o carga.')
    if initial_soc_pct < min_soc_pct:
        warnings.append('El estado de carga inicial está por debajo del SOC mínimo permitido por la profundidad de descarga. La energía disponible quedó en 0 Wh.')
    if total_load_power_w > 0 and total_battery_ac_usable_wh > 0:
        c_rate = total_load_power_w / max(total_battery_nominal_wh, 1e-9)
        if c_rate > 0.5:
            warnings.append('La carga instantánea es alta respecto a la energía nominal del banco. En un sistema real esto puede reducir autonomía y exigir más corriente a la batería/inversor.')
    if total_load_power_w == 0:
        warnings.append('La potencia total de carga es 0 W; por eso no se calculó autonomía instantánea.')
    if total_load_daily_wh == 0:
        warnings.append('El consumo diario es 0 Wh/día; revisa las horas por día de los equipos.')
    if total_panel_power_w == 0:
        warnings.append('No agregaste paneles solares válidos. El análisis híbrido se comportará como batería sola.')

    formulas = {
        'battery_nominal_wh': 'Wh_batería = Voltaje × Ah × Cantidad',
        'battery_usable_wh': 'Wh_útiles_AC = Wh_nominal × fracción_SOC_utilizable × eficiencia_descarga × eficiencia_inversor',
        'load_daily_wh': 'Wh_día = Potencia_W × horas_por_día × cantidad',
        'solar_daily_wh': 'Wh_solar_día = W_paneles × horas_solares_pico × eficiencia_solar × eficiencia_inversor',
        'battery_hours': 'Autonomía_horas = Wh_útiles_AC / W_carga_instantánea',
        'hybrid_days': 'Autonomía_días_híbrido = Wh_útiles_AC / déficit_diario_Wh',
    }

    return {
        'batteries': batteries,
        'appliances': appliances,
        'panels': panels,
        'inputs': payload['inputs'],
        'summary': {
            'total_battery_nominal_wh': total_battery_nominal_wh,
            'min_soc_pct': min_soc_pct,
            'accessible_soc_pct': accessible_soc_pct,
            'total_battery_ac_usable_wh': total_battery_ac_usable_wh,
            'total_panel_power_w': total_panel_power_w,
            'solar_daily_useful_wh': solar_daily_useful_wh,
            'total_load_power_w': total_load_power_w,
            'total_load_daily_wh': total_load_daily_wh,
            'battery_only_hours': battery_only_hours,
            'battery_only_days_by_profile': battery_only_days_by_profile,
            'daily_balance_wh': daily_balance_wh,
            'hybrid_days': hybrid_days,
            'solar_status': solar_status,
        },
        'appliance_rows': appliance_rows,
        'warnings': warnings,
        'formulas': formulas,
    }


@app.template_filter('num')
def fmt_num(value: Any) -> str:
    if value is None:
        return '—'
    try:
        number = float(value)
        return f'{number:,.2f}'
    except (TypeError, ValueError):
        return str(value)


@app.template_filter('duration')
def fmt_duration(value: Any) -> str:
    if value is None:
        return '—'
    try:
        return format_duration_hours(float(value))
    except (TypeError, ValueError):
        return '—'


@app.route('/', methods=['GET', 'POST'])
def index():
    payload = default_payload() if request.method == 'GET' else extract_payload_from_request()
    results = calculate(payload)
    return render_template('index.html', payload=payload, results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
