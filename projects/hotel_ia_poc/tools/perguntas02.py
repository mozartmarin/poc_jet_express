from tabulate import tabulate
import datetime
import pandas as pd
import re

TOTAL_QUARTOS = 100


# === Indicadores diretos ===

def get_taxa_ocupacao_hoje(df):
    hoje = datetime.date.today()
    ocupados = df.copy()
    ocupados = ocupados[
        (ocupados["data_checkin"] <= hoje) &
        (ocupados["data_checkout"] > hoje) &
        (ocupados["status"].str.lower() == "confirmado")
    ]
    taxa = (len(ocupados) / TOTAL_QUARTOS) * 100
    return f"A taxa de ocupação hoje é de {taxa:.1f}%."


def get_checkins_hoje(df):
    hoje = datetime.date.today()
    checkins = df.copy()
    checkins = checkins[
        (checkins["data_checkin"] == hoje) &
        (checkins["status"].str.lower() == "confirmado")
    ]
    return f"Temos {len(checkins)} check-ins previstos para hoje."


def get_checkouts_hoje(df):
    hoje = datetime.date.today()
    checkouts = df.copy()
    checkouts = checkouts[
        (checkouts["data_checkout"] == hoje) &
        (checkouts["status"].str.lower() == "confirmado")
    ]
    return f"Temos {len(checkouts)} check-outs previstos para hoje."


def get_diaria_media(df, input_str="semana"):
    hoje = datetime.date.today()
    if "mes" in input_str.lower():
        inicio = hoje.replace(day=1)
    elif "semana" in input_str.lower():
        inicio = hoje - datetime.timedelta(days=7)
    else:
        inicio = hoje - datetime.timedelta(days=30)

    periodo = df.copy()
    periodo = periodo[
        (periodo["data_checkin"] >= inicio) &
        (periodo["data_checkin"] <= hoje) &
        (periodo["status"].str.lower() == "confirmado")
    ]

    media = periodo["valor_diaria"].mean()
    return f"A diária média no período selecionado é de R$ {media:.2f}."


def get_permanencia_media(df, input_str="semana"):
    hoje = datetime.date.today()
    if "mes" in input_str.lower():
        inicio = hoje.replace(day=1)
    elif "semana" in input_str.lower():
        inicio = hoje - datetime.timedelta(days=7)
    else:
        inicio = hoje - datetime.timedelta(days=30)

    periodo = df.copy()
    periodo = periodo[
        (periodo["data_checkin"] >= inicio) &
        (periodo["data_checkin"] <= hoje) &
        (periodo["status"].str.lower() == "confirmado")
    ]
    if periodo.empty:
        return "Nenhuma permanência registrada no período."
    
    periodo["permanencia"] = (periodo["data_checkout"] - periodo["data_checkin"]).dt.days
    media = periodo["permanencia"].mean()
    return f"A permanência média dos hóspedes é de {media:.1f} dias."


# === Auxiliar de datas ===

def _parse_data_br(input_str):
    input_str = input_str.strip().lower().replace("–", "-").replace("—", "-").strip('"').strip("'")
    if "hoje" in input_str: return datetime.date.today()
    if "amanha" in input_str: return datetime.date.today() + datetime.timedelta(days=1)
    if "ontem" in input_str: return datetime.date.today() - datetime.timedelta(days=1)

    input_str = input_str.split()[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try: return datetime.datetime.strptime(input_str, fmt).date()
        except ValueError: continue
    return None


# === Listagens ===

def listar_checkins_por_data(df, input_str="01/05/2025"):
    data = _parse_data_br(input_str)
    if not data:
        return "Data inválida. Use o formato DD/MM/AAAA."

    checkins = df.copy()
    checkins = checkins[
        (checkins["data_checkin"] == data) &
        (checkins["status"].str.lower() == "confirmado")
    ]
    if checkins.empty:
        return f"Nenhum check-in encontrado para {input_str}."
    nomes = checkins["nome_hospede"].tolist()
    return f"Hóspedes com check-in em {input_str}:\n" + "\n".join(f"- {nome}" for nome in nomes)


def listar_checkouts_por_data(df, input_str="02/05/2025"):
    data = _parse_data_br(input_str)
    if not data:
        return "Data inválida. Use o formato DD/MM/AAAA."

    checkouts = df.copy()
    checkouts = checkouts[
        (checkouts["data_checkout"] == data) &
        (checkouts["status"].str.lower() == "confirmado")
    ]
    if checkouts.empty:
        return f"Nenhum check-out encontrado para {input_str}."
    nomes = checkouts["nome_hospede"].tolist()
    return f"Hóspedes com check-out em {input_str}:\n" + "\n".join(f"- {nome}" for nome in nomes)


def listar_hospedes_por_periodo(df, input_str="01/05/2025 a 03/05/2025"):
    input_str = input_str.lower().strip()
    input_str = input_str.replace("–", "-").replace("—", "-").replace(" to ", " a ").replace(" - ", " a ").replace(",", " a")
    datas = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", input_str)
    if len(datas) != 2:
        return "Formato inválido. Use: DD/MM/AAAA a DD/MM/AAAA"

    data_inicial = _parse_data_br(datas[0])
    data_final = _parse_data_br(datas[1])
    if not data_inicial or not data_final:
        return "Datas inválidas. Use o formato DD/MM/AAAA."

    periodo = df.copy()
    periodo = periodo[
        (periodo["data_checkin"] <= data_final) &
        (periodo["data_checkout"] >= data_inicial) &
        (periodo["status"].str.lower() == "confirmado")
    ]
    if periodo.empty:
        return "Nenhum hóspede hospedado no período informado."

    nomes = periodo["nome_hospede"].tolist()
    return (
        f"Hóspedes hospedados entre {data_inicial.strftime('%d/%m/%Y')} e {data_final.strftime('%d/%m/%Y')}:\n" +
        "\n".join(f"- {nome}" for nome in nomes)
    )


# === Consulta dinâmica ===

def consultar_reservas(df, input_str: str):
    hoje = datetime.date.today()
    amanha = hoje + datetime.timedelta(days=1)
    input_str_lower = input_str.lower().strip()

    if "checkout amanhã" in input_str_lower:
        resultado = df[df["data_checkout"] == amanha]
    elif "checkin amanhã" in input_str_lower:
        resultado = df[df["data_checkin"] == amanha]
    elif "cancelado" in input_str_lower:
        resultado = df[df["status"].str.lower() == "cancelado"]
    elif "confirmado" in input_str_lower:
        resultado = df[df["status"].str.lower() == "confirmado"]
    else:
        query = input_str_lower.replace("reservas com", "").strip()
        query = re.sub(r"valor[ _]di(a|á)ria", "valor_diaria", query)
        query = re.sub(r"h[oó]spedes", "numero_hospedes", query)

        try:
            resultado = df.query(query)
        except Exception as e:
            return f"Erro ao interpretar a consulta: {e}"

    if resultado.empty:
        return "Nenhum resultado encontrado."

    linhas = []
    for _, row in resultado.iterrows():
        linha = (
            f"- **{row['nome_hospede']}**  \n"
            f"  Check-in: {row['data_checkin'].strftime('%d/%m/%Y')} • "
            f"Check-out: {row['data_checkout'].strftime('%d/%m/%Y')} • "
            f"Status: {row['status']} • "
            f"Diária: R$ {row['valor_diaria']:.2f}".replace(".", ",")
        )
        if 'numero_hospedes' in row:
            linha += f" • Hóspedes: {row['numero_hospedes']}"
        linhas.append(linha)

    return "\n".join(linhas)
