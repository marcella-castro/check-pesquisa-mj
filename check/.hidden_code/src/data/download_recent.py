#!/usr/bin/env python3
"""
Wrapper para baixar respostas dos últimos N dias usando LimeSurveyAPI e filtrar localmente.

Uso:
  python download_recent.py --days 15 --out exports/processos_recent.csv

Ele baixa os surveys da categoria 'processo' por padrão, filtra por colunas de data plausíveis
e concatena o resultado em um CSV de saída.
"""

from datetime import datetime, timedelta
from pathlib import Path
import argparse
import pandas as pd
from typing import List

from .lime_api import LimeSurveyAPI


DATE_COL_KEYWORDS = ['submit', 'start', 'data', 'date', 'hora', 'time']


def find_date_column(df: pd.DataFrame) -> List[str]:
    """Retorna lista de colunas plausíveis que contenham datas."""
    candidates = [c for c in df.columns if any(k in c.lower() for k in DATE_COL_KEYWORDS)]
    # preferir submit/start
    preferred = [c for c in candidates if 'submit' in c.lower() or 'start' in c.lower()]
    if preferred:
        return preferred
    return candidates


def filter_recent(df: pd.DataFrame, since: datetime) -> pd.DataFrame:
    if df.empty:
        return df

    date_cols = find_date_column(df)
    if not date_cols:
        # sem colunas de data reconhecíveis -> não filtrar
        return pd.DataFrame()

    # tentar cada coluna até encontrar datas válidas
    for col in date_cols:
        ts = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        if ts.notna().any():
            mask = ts >= since
            return df[mask].copy()

    return pd.DataFrame()


def download_last_days(days: int = 15, out_dir: str = 'exports') -> None:
    since = datetime.now() - timedelta(days=days)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    api = LimeSurveyAPI()
    if not api.get_session_key():
        print('Nao foi possivel iniciar sessao com LimeSurvey; abortando.')
        return

    try:
        survey_ids = api.survey_ids.get('processo', [])
        all_dfs = []

        for sid in survey_ids:
            print(f'Download survey {sid} ...')
            df = api.download_survey_data(sid)
            if df.empty:
                print(f'  sem registros no survey {sid} (ou falha).')
                continue

            recent = filter_recent(df, since)
            if recent.empty:
                print(f'  nenhum registro recente nos ultimos {days} dias para survey {sid}.')
                continue

            # salvar CSV por survey
            fname = out_path / f'processo_{sid}_last{days}d.csv'
            recent.to_csv(fname, index=False)
            print(f'  salvos {len(recent)} registros em {fname}')

            all_dfs.append(recent)

        # concatenar tudo e salvar resumo
        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            combined_file = out_path / f'processo_last{days}d_combined.csv'
            combined.to_csv(combined_file, index=False)
            print(f'Arquivo combinado salvo em: {combined_file} (total registros: {len(combined)})')
        else:
            print('Nenhum registro recente encontrado nos surveys de processo.')

    finally:
        api.release_session_key()


def main():
    parser = argparse.ArgumentParser(description='Baixa respostas dos ultimos N dias (categoria processo)')
    parser.add_argument('--days', type=int, default=15, help='Número de dias (padrão 15)')
    parser.add_argument('--out', type=str, default='exports', help='Diretório de saída')
    args = parser.parse_args()

    download_last_days(days=args.days, out_dir=args.out)


if __name__ == '__main__':
    main()
