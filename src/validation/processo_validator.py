"""
Validador para dados de processo judicial
"""

import pandas as pd
import re
from typing import List, Dict, Any
from config.settings import Config

class ProcessoValidator:
    def __init__(self):
        # Padrões de validação
        self.padrao_controle = re.compile(r'^\d{1,4}[RV]0[1-9]$')
        self.padrao_processo = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$')
        
    def validate(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida dados do processo
        
        Args:
            df: DataFrame com dados do processo
            
        Returns:
            Lista de erros encontrados em formato de dicionário
        """
        erros = []
        
        # P0Q1 - Validar número de controle
        erros.extend(self._validate_numero_controle(df))
        
        # P0Q2 - Validar número do processo
        erros.extend(self._validate_numero_processo(df))
        
        # Verificação específica: todo número de processo deve ter ao menos um R01
        erros.extend(self._validate_processo_tem_R01(df))
        
        # Verificação de duplicidade da combinação controle + vítima
        erros.extend(self._validate_duplicidade_controle_vitima(df))
        
        # Verificação de consistência entre número de réus
        erros.extend(self._validate_consistencia_reus(df))

        erros.extend(self._validate_consistencia_reus_suspeitos(df))

        erros.extend(self._validate_consistencia_vitimas(df))

        # Verificação de depoimento de testemunha
        erros.extend(self._validate_depoimento_testemunha(df))

        # Verificar se existem todos os números de controle para os réus com trânsito em julgado
        erros.extend(self._validate_sequencia_controle_reus(df))

        # Verificar tipos penais na denúncia
        erros.extend(self._validate_tipos_penais_denuncia(df))

        # Verificar cronologia entre marcos processuais
        erros.extend(self._validate_cronologia_datas(df))

        # Verificar tempo MAIOR QUE UM ANO entre crime e flagrante
        erros.extend(self._validate_tempo_crime_flagrante(df))
        
        # Outras validações podem ser adicionadas aqui
        erros.extend(self._validate_campos_obrigatorios(df))
        
        return erros
    
    def _validate_numero_controle(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        P0Q1. Número de controle (dado pela equipe) - Teste por padrão de resposta
        Padrão esperado: até 4 dígitos + R/V + 0 + 1 dígito (ex: 123R01, 1V09)
        """
        erros = []
        coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
        
        if coluna_controle not in df.columns:
            return erros
        
        # Filtrar linhas com erro
        linhas_com_erro = df[~df[coluna_controle].astype(str).str.match(self.padrao_controle, na=False)]
        
        # Criar o log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                'Nº de Controle': row.get(coluna_controle, 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': coluna_controle,
                'Tipo de Erro': 'Formato Inválido',
                'Valor Encontrado': row.get(coluna_controle, 'N/A'),
                'Regra Violada / Esperado': 'Padrão: até 4 dígitos + [R/V] + 0 + 1 dígito (ex: 123R01, 45V09)',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_numero_processo(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        P0Q2. Número do Processo - Validar formato CNJ
        Padrão esperado: 0000000-00.0000.0.00.0000
        """
        erros = []
        coluna_processo = 'P0Q2. Número do Processo:'
        
        if coluna_processo not in df.columns:
            return erros
        
        # Filtrar linhas com erro de formato
        linhas_com_erro = df[~df[coluna_processo].astype(str).str.match(self.padrao_processo, na=False)]
        
        # Criar o log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get(coluna_processo, 'N/A'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': coluna_processo,
                'Tipo de Erro': 'Formato Inválido',
                'Valor Encontrado': row.get(coluna_processo, 'N/A'),
                'Regra Violada / Esperado': 'Formato CNJ: 0000000-00.0000.0.00.0000',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_processo_tem_R01(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida se todo número de processo tem ao menos um R01 associado
        """
        erros = []
        coluna_processo = 'P0Q2. Número do Processo:'
        coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
        
        if coluna_processo not in df.columns or coluna_controle not in df.columns:
            return erros
            
        # Filtrar linhas com valores válidos nas duas colunas
        df_validos = df.dropna(subset=[coluna_processo, coluna_controle])
        
        # Filtrar números de controle que seguem o padrão válido (dígitos + R + dígitos)
        padrao_valido = r'^\d{1,4}R\d{2}$'
        df_validos = df_validos[df_validos[coluna_controle].astype(str).str.match(padrao_valido)]
        
        # Verificar se controle termina em R01
        df_validos['termina_em_R01'] = df_validos[coluna_controle].astype(str).str.match(r'^\d{1,4}R01$')
        
        # Agrupar por processo e verificar se existe ao menos um com R01
        processos_com_R01 = df_validos[df_validos['termina_em_R01']][coluna_processo].unique()
        processos_todos = df_validos[coluna_processo].unique()
        
        # Obter os que estão no total mas não têm nenhum R01
        processos_sem_R01 = set(processos_todos) - set(processos_com_R01)
        
        # Filtrar linhas com erro (um representante para cada processo sem R01)
        linhas_com_erro = df_validos[df_validos[coluna_processo].isin(processos_sem_R01)]
        
        # Criar o log dos erros (apenas um por processo)
        processos_já_registrados = set()
        
        for _, row in linhas_com_erro.iterrows():
            processo_atual = row.get(coluna_processo, 'N/A')
            
            # Evita registrar o mesmo processo mais de uma vez
            if processo_atual in processos_já_registrados:
                continue
                
            processos_já_registrados.add(processo_atual)
            
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': processo_atual,
                'Nº de Controle': row.get(coluna_controle, 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': coluna_controle,
                'Tipo de Erro': 'Ausência de número de controle com R01',
                'Valor Encontrado': row.get(coluna_processo, 'N/A'),
                'Regra Violada / Esperado': 'Todo número de processo deve ter ao menos um número de controle terminando em R01',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_duplicidade_controle_vitima(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Verifica se a combinação Número de Controle e Vítima é única na base
        """
        erros = []
        coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
        coluna_vitima = 'P0Q1A. Número de controle para casos em que há mais de uma vítima:'
        
        if coluna_controle not in df.columns or coluna_vitima not in df.columns:
            return erros
        
        # Criar uma cópia para não modificar o DataFrame original
        df_temp = df.copy()
        
        # Garantir que os campos sejam strings
        df_temp[coluna_controle] = df_temp[coluna_controle].astype(str).str.strip()
        df_temp[coluna_vitima] = df_temp[coluna_vitima].astype(str).str.strip()
        
        # Criar chave combinada para detecção de duplicatas
        df_temp['chave_controle'] = df_temp[coluna_controle] + ' | ' + df_temp[coluna_vitima]
        
        # Identificar duplicatas
        duplicatas = df_temp[df_temp.duplicated(subset=['chave_controle'], keep=False)]
        
        # Log dos erros
        for _, row in duplicatas.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'Desconhecido')}",
                'ID da Resposta': row.get('id', 'Não encontrado'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'Não disponível'),
                'Nº de Controle': row.get(coluna_controle, 'Não disponível'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': f'{coluna_controle} + {coluna_vitima}',
                'Tipo de Erro': 'Duplicação da combinação entre controle principal e controle de vítima',
                'Valor Encontrado': f"{row[coluna_controle]} + {row[coluna_vitima]}",
                'Regra Violada / Esperado': 'Cada combinação de número de controle e controle de vítima deve ser única na base',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_consistencia_reus(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida consistência entre número de réus total e com trânsito em julgado
        """
        erros = []
        coluna_controle0 = 'P0Q14. Número de réus no processo:'
        coluna_controle1 = 'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo'
        
        if coluna_controle0 not in df.columns or coluna_controle1 not in df.columns:
            return erros
        
        # Converter para numérico para comparação
        df_temp = df.copy()
        df_temp[coluna_controle0] = pd.to_numeric(df_temp[coluna_controle0], errors='coerce')
        df_temp[coluna_controle1] = pd.to_numeric(df_temp[coluna_controle1], errors='coerce')
        
        # Identificar linhas com erro
        linhas_com_erro = df_temp[
            (df_temp[coluna_controle0] != 0) &
            (df_temp[coluna_controle0].notna()) &
            (df_temp[coluna_controle1].notna()) &
            (df_temp[coluna_controle1] > df_temp[coluna_controle0])
        ]
        
        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'Desconhecido')}",
                'ID da Resposta': row.get('id', 'Não encontrado'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'Não disponível'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'Não disponível'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': f"{coluna_controle0} E {coluna_controle1}",
                'Tipo de Erro': 'Valores inconsistentes',
                'Valor Encontrado': f"Réus total: {row[coluna_controle0]} e Réus com TJ: {row[coluna_controle1]}",
                'Regra Violada / Esperado': 'O No de Réus com TJ não pode ser maior que o No Réus Total.',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_consistencia_reus_suspeitos(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida consistência entre número de réus total e número de suspeitos
        """
        erros = []
        coluna_controle0 = 'P0Q14. Número de réus no processo:'
        coluna_controle1 = 'P0Q17. Quantos suspeitos foram apontados e identificados pela polícia?'
        
        if coluna_controle0 not in df.columns or coluna_controle1 not in df.columns:
            return erros
        
        # Converter para numérico para comparação
        df_temp = df.copy()
        df_temp[coluna_controle0] = pd.to_numeric(df_temp[coluna_controle0], errors='coerce')
        df_temp[coluna_controle1] = pd.to_numeric(df_temp[coluna_controle1], errors='coerce')
        
        # Identificar linhas com erro
        linhas_com_erro = df_temp[
            (df_temp[coluna_controle0] != 0) &
            (df_temp[coluna_controle0].notna()) &
            (df_temp[coluna_controle1].notna()) &
            (df_temp[coluna_controle1] < df_temp[coluna_controle0])
        ]
        
        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'Desconhecido')}",
                'ID da Resposta': row.get('id', 'Não encontrado'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'Não disponível'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'Não disponível'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': f"{coluna_controle0} E {coluna_controle1}",
                'Tipo de Erro': 'Valores inconsistentes',
                'Valor Encontrado': f"Réus total: {row[coluna_controle0]} e Suspeitos apontados: {row[coluna_controle1]}",
                'Regra Violada / Esperado': 'O No de Suspeitos não pode ser maior que o No Réus Total.',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
    
    def _validate_consistencia_vitimas(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida consistência entre número de vítimas identificadas e não identificadas pela polícia
        """
        erros = []
        coluna_controle0 = 'P0Q18. Qual o número de vítimas no processo?'
        coluna_controle1 = 'P0Q20. Quantas vítimas NÃO foram identificadas pela polícia?'
        
        if coluna_controle0 not in df.columns or coluna_controle1 not in df.columns:
            return erros
        
        # Converter para numérico para comparação
        df_temp = df.copy()
        df_temp[coluna_controle0] = pd.to_numeric(df_temp[coluna_controle0], errors='coerce')
        df_temp[coluna_controle1] = pd.to_numeric(df_temp[coluna_controle1], errors='coerce')
        
        # Identificar linhas com erro
        linhas_com_erro = df_temp[
            (df_temp[coluna_controle0] != 0) &
            (df_temp[coluna_controle0].notna()) &
            (df_temp[coluna_controle1].notna()) &
            (df_temp[coluna_controle1] > df_temp[coluna_controle0])
        ]
        
        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'Desconhecido')}",
                'ID da Resposta': row.get('id', 'Não encontrado'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'Não disponível'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'Não disponível'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': f"{coluna_controle1}" ,
                'Tipo de Erro': 'Valores inconsistentes',
                'Valor Encontrado': f"Vítimas Total: {row[coluna_controle0]} e Vítimas Não Identificadas: {row[coluna_controle1]}",
                'Regra Violada / Esperado': 'O No de Vítimas Não Identificadas não pode ser maior que o No de Vítimas Total',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros
   
    def _validate_depoimento_testemunha(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        P6Q6[SQ009]. Verifica se há depoimentos de testemunhas juntados ao processo
        Emite um alerta quando não há depoimento de testemunha, pois é incomum
        """

        erros = []
        coluna_controle = 'P6Q6[SQ009]'

        if coluna_controle not in df.columns:
            return erros
            
        # Filtrar linhas onde não há depoimento de testemunha
        linhas_com_erro = df[df[coluna_controle] == "Não"]

        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': coluna_controle,
                'Tipo de Erro': '[ALERTA] Ausência de depoimento de testemunha',
                'Valor Encontrado': row.get(coluna_controle, 'N/A'),
                'Regra Violada / Esperado': 'Sem depoimento de testemunha como diligência processual',
                'Categoria': 'processo'
            }
            erros.append(erro)

        return erros

    def _validate_sequencia_controle_reus(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Verifica se para cada número de réus com trânsito em julgado existem as respectivas linhas de controle
        Por exemplo, se há 3 réus com trânsito em julgado, devem existir os controles XXXR01, XXXR02 e XXXR03
        """
        erros = []
        coluna_qtd_reus = 'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo'
        coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
        
        if coluna_qtd_reus not in df.columns or coluna_controle not in df.columns:
            return erros
            
        padrao_controle = re.compile(r'^\d{1,4}R\d{2}$')
        
        for _, row in df[df[coluna_qtd_reus].notna()].iterrows():
            try:
                num_reus = int(row[coluna_qtd_reus])
            except ValueError:
                continue
                
            if num_reus <= 1:
                continue
                
            controle_cheio = str(row[coluna_controle]).strip()
            
            if not padrao_controle.match(controle_cheio):
                continue  # pula se o controle atual estiver fora do padrão esperado
                
            # Ex: de 123R01 pega 123R como base
            controle_base = controle_cheio[:-2]
            
            # Controles esperados: 123R01, 123R02, ..., 123R0n
            controles_esperados = [f"{controle_base}{i:02d}" for i in range(1, num_reus + 1)]
            
            # Filtra controles válidos da base
            controles_validos = df[coluna_controle].dropna().astype(str).tolist()
            controles_validos = [c for c in controles_validos if padrao_controle.match(c)]
            
            # Identifica os que estão faltando
            controles_faltando = [c for c in controles_esperados if c not in controles_validos]
            
            # Se houver algum faltando, adiciona uma única entrada no log
            if controles_faltando:
                faltando_formatado = ", ".join(controles_faltando)
                erro = {
                    'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                    'ID da Resposta': row.get('id', 'N/A'),
                    'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                    'Nº de Controle': row.get(coluna_controle, 'N/A'),
                    'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                    'Campo': coluna_controle,
                    'Tipo de Erro': 'Números de controle ausentes ou inválidos',
                    'Valor Encontrado': f"Nº de Réus: {num_reus}. Formulários Faltando: {faltando_formatado}",
                    'Regra Violada / Esperado': f'Os seguintes números de controle esperados para {num_reus} réus não foram encontrados na base: {faltando_formatado}',
                    'Categoria': 'processo'
                }
                erros.append(erro)
        
        return erros

    def _validate_tipos_penais_denuncia(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida se os tipos penais indicados na denúncia foram devidamente preenchidos.
        Gera um alerta quando não há qualificação específica (apenas "outros" ou nenhuma opção).
        """
        erros = []
        
        # Colunas com as alternativas de tipos penais
        colunas_tipos = [
            "P4Q8[SQ001]",  # Homicídio Simples
            "P4Q8[SQ002]",  # Homicídio Privilegiado
            "P4Q8[SQ003]",  # Homicídio Qualificado
            "P4Q8[SQ004]",  # Homicídio Contra Autoridade ou Agente de Segurança Pública
            "P4Q8[SQ005]",  # Homicídio Qualificado Contra Menor de 14 Anos
            "P4Q8[SQ006]",  # Homicídio Agravado pelo Extermínio de Seres Humanos
            "P4Q8[SQ007]",  # Feminicídio
            "P4Q8[other]"   # Outros
        ]
        
        # Verifica se as colunas existem no DataFrame
        colunas_existentes = [col for col in colunas_tipos if col in df.columns]
        if not colunas_existentes:
            return erros
        
        # Filtra registros onde nenhuma opção específica foi marcada (só "outros" ou nenhuma)
        opcoes_especificas = colunas_tipos[:-1]  # Todas exceto "Outros"
        
        # Criar máscaras para filtrar linhas onde nenhuma opção específica está marcada
        mascara_nenhuma_opcao = pd.Series(True, index=df.index)
        for col in opcoes_especificas:
            if col in df.columns:
                mascara_nenhuma_opcao &= (df[col].isna() | (df[col] == "Não") | (df[col] == ""))
        
        # Filtrar linhas com problema (nenhuma opção específica marcada)
        linhas_com_erro = df[mascara_nenhuma_opcao]
        
        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            valor_outros = row.get("P4Q8[other]", "Não preenchido")
            
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': "P4Q8",
                'Tipo de Erro': '[ALERTA] Sem Preenchimento ou Apenas Outros na Qualificação da Denúncia',
                'Valor Encontrado': f"Outros: {valor_outros}",
                'Regra Violada / Esperado': 'Sem preenchimento adequado sobre a Qualificação da Denúncia.',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros 
    
    def _validate_cronologia_datas(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida a ordem cronológica entre todas as combinações de datas processuais preenchidas.
        Verifica se os marcos processuais estão em ordem temporal correta.
        """
        erros = []
        
        # Definir os marcos processuais em ordem cronológica esperada (nome amigável: nome da coluna)
        marcos_processuais = {
        'Data do Crime': 'P1Q1. Qual a data do crime?',
        'Data abertura IP': 'P3Q1. Data da abertura do Inquérito Policial:',
        'Data Relatório Final IP': 'P3Q28. Data do relatório final do Inquérito Policial:',
        'Data oferecimento da Denúncia': 'P4Q7. Data do oferecimento da denúncia:',
        'Data decisão imediatamente após Denúncia': 'P4Q14. Qual a data da decisão/despacho do juiz imediatamente após a denúncia?',
        'Data do Recebimento da Denúncia': 'P6Q0. Qual a data em que a denúncia foi recebida?',
        'Data 1a AIJ': 'P6Q1. Data da primeira audiência de instrução realizada:',
        'Data última AIJ': 'P6Q3. Se sim, qual a data da última audiência de instrução realizada?',
        'Data decisão 1a fase do Juri': 'P7Q2. Data da decisão que finaliza a primeira fase do Júri:',
        'Data nova decisão da 1a Fase': 'P7Q31. Data da nova decisão de primeira fase',
        'Data agendamento audiência Juri': 'P8Q0. Primeira data de agendamento da audiência de júri:',
        'Data realização audiência Júri': 'P8Q4. Data em que a audiência de júri foi realizada:',
        'Data prolação sentença de júri': 'P8Q20. Data em que a sentença de júri foi prolatada:',
        'Data nova decisão de 2a fase': 'P8Q57. Qual a data da nova decisão de segunda fase?',
        'Data do trânsito em julgado': 'P9Q1. Data do trânsito em julgado da sentença:',
        'Data do arquivamento definitivo': 'P9Q2. Data do arquivamento definitivo do processo:'
        }
        
        # Converter todas as datas para datetime
        df_temp = df.copy()
        colunas_datas = list(marcos_processuais.values())
        
        for col in colunas_datas:
            if col in df_temp.columns:
                df_temp[col] = pd.to_datetime(df_temp[col], errors='coerce', dayfirst=True)
        
        # Criar mapeamento inverso (coluna -> nome amigável)
        coluna_para_nome = {v: k for k, v in marcos_processuais.items()}
        
        # Processar cada linha individualmente
        for _, row in df_temp.iterrows():
            # Identificar quais datas estão preenchidas nesta linha
            datas_preenchidas = []
            for i, col in enumerate(colunas_datas):
                if col in df_temp.columns and pd.notna(row[col]):
                    datas_preenchidas.append((i, col, row[col]))
            
            # Se há menos de 2 datas preenchidas, não há o que comparar
            if len(datas_preenchidas) < 2:
                continue
            
            # Verificar todas as combinações de datas preenchidas
            for i in range(len(datas_preenchidas)):
                for j in range(i + 1, len(datas_preenchidas)):
                    idx_anterior, col_anterior, data_anterior = datas_preenchidas[i]
                    idx_posterior, col_posterior, data_posterior = datas_preenchidas[j]
                    
                    # Verificar se a ordem cronológica está incorreta
                    if data_posterior < data_anterior:
                        nome_anterior = coluna_para_nome[col_anterior]
                        nome_posterior = coluna_para_nome[col_posterior]
                        
                        # Criar entrada de erro
                        erro = {
                            'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                            'ID da Resposta': row.get('id', 'N/A'),
                            'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                            'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                            'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                            'Campo': f'{nome_posterior} < {nome_anterior}',
                            'Tipo de Erro': 'Ordem cronológica incorreta',
                            'Valor Encontrado': f"{data_anterior.date()} → {data_posterior.date()}",
                            'Regra Violada / Esperado': f'{nome_anterior} deve ser anterior a {nome_posterior}',
                            'Categoria': 'processo'
                        }
                        erros.append(erro)
        
        return erros
    
    def _validate_tempo_crime_flagrante(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Verifica se o tempo entre a data do crime e a prisão em flagrante é maior que um ano.
        Emite um alerta quando esse período é excessivo, pois é incomum para prisões em flagrante.
        """
        erros = []
        
        # Nomes das colunas
        col_data_anterior = 'P0Q21. Data do crime:'
        col_data_posterior = 'P1Q2. Data da prisão em flagrante:'
        col_verificacao = 'P1Q1. Houve prisão em flagrante desse réu?'
        
        # Verificar se todas as colunas necessárias existem
        if not all(col in df.columns for col in [col_data_anterior, col_data_posterior, col_verificacao]):
            return erros
        
        # Criar cópia para não modificar o DataFrame original
        df_temp = df.copy()
        
        # Converter as datas para datetime
        df_temp[col_data_anterior] = pd.to_datetime(df_temp[col_data_anterior], errors='coerce', dayfirst=True)
        df_temp[col_data_posterior] = pd.to_datetime(df_temp[col_data_posterior], errors='coerce', dayfirst=True)
        
        # Filtrar linhas com erro: prisão em flagrante com mais de um ano após o crime
        linhas_com_erro = df_temp[
            (df_temp[col_verificacao] == 'Sim') &
            df_temp[col_data_anterior].notna() &
            df_temp[col_data_posterior].notna() &
            ((df_temp[col_data_posterior] - df_temp[col_data_anterior]).dt.days > 364)
        ]
        
        # Gerar log dos erros
        for _, row in linhas_com_erro.iterrows():
            data_crime = row[col_data_anterior].date() if pd.notna(row[col_data_anterior]) else 'N/A'
            data_flagrante = row[col_data_posterior].date() if pd.notna(row[col_data_posterior]) else 'N/A'
            
            erro = {
                'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': f'{col_data_posterior} > {col_data_anterior}',
                'Tipo de Erro': '[ALERTA] Tempo excessivo entre crime e flagrante',
                'Valor Encontrado': f"{data_crime} → {data_flagrante}",
                'Regra Violada / Esperado': 'Prisão em flagrante mais de um ano depois do crime',
                'Categoria': 'processo'
            }
            erros.append(erro)
        
        return erros

    def _validate_campos_obrigatorios(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida campos obrigatórios básicos
        """
        erros = []
        
        campos_obrigatorios = [
            'P0Q0. Pesquisador responsável pelo preenchimento:',
            'P0Q1. Número de controle (dado pela equipe)',
            'P0Q2. Número do Processo:'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in df.columns:
                continue
                
            # Verificar campos vazios ou nulos
            linhas_vazias = df[df[campo].isna() | (df[campo].astype(str).str.strip() == '')]
            
            for _, row in linhas_vazias.iterrows():
                erro = {
                    'Formulário': f"Processo {row.get('form_origem', 'N/A')}",
                    'ID da Resposta': row.get('id', 'N/A'),
                    'Nº Processo': row.get('P0Q2. Número do Processo:', 'N/A'),
                    'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                    'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                    'Campo': campo,
                    'Tipo de Erro': 'Campo Obrigatório Vazio',
                    'Valor Encontrado': 'Vazio/Nulo',
                    'Regra Violada / Esperado': 'Campo deve ser preenchido',
                    'Categoria': 'processo'
                }
                erros.append(erro)
        
        return erros
