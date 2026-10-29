import json
import platform
import sklearn
import numpy
import joblib
import numpy as np
import pandas as pd

from src.data_model.config import FEATURES, OUTPUT_DIR, SEED


def json_ready(value):
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]

    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())

    if isinstance(value, (np.floating, np.integer)):
        return value.item()

    if isinstance(value, np.bool_):
        return bool(value)

    if pd.isna(value):
        return None

    return value


def build_metadata(familia, busca, metrics, n_combinacoes):
    importances = getattr(busca.best_estimator_, "feature_importances_", None)

    if importances is None:
        feature_importances = {}
    else:
        feature_importances = {
            feature: float(score)
            for feature, score in zip(FEATURES, importances)
        }

    return {
        "nome": f"NetPulse {familia.replace('_', ' ').title()}",
        "versao": "1.0.0",
        "ambiente": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": numpy.__version__,
            "pandas": pd.__version__,
            "joblib": joblib.__version__,
        },
        "familia": familia,
        "seed": SEED,
        "features": list(FEATURES),
        "entradas": [
            {
                "nome": "perda_pct",
                "tipo": "float",
                "descricao": "Percentual de perda de pacotes."
            },
            {
                "nome": "aumento_pct",
                "tipo": "float",
                "descricao": "Variação percentual do RTT em relação à mediana do baseline."
            },
            {
                "nome": "z_robusto",
                "tipo": "float",
                "descricao": "Desvio robusto do RTT em relação ao baseline."
            },
            {
                "nome": "jitter_atual",
                "tipo": "float",
                "descricao": "Média das diferenças absolutas entre RTTs válidos consecutivos."
            },
            {
                "nome": "jitter_relativo",
                "tipo": "float",
                "descricao": "Relação entre o jitter atual e o jitter típico do baseline."
            },
            {
                "nome": "timeout_atual",
                "tipo": "int",
                "descricao": "Indicador de timeout: 1 para timeout e 0 caso contrário."
            },
            {
                "nome": "n5_timeout",
                "tipo": "int",
                "descricao": "Quantidade de timeouts nas últimas cinco medições."
            },
            {
                "nome": "n5_aumento80",
                "tipo": "int",
                "descricao": "Quantidade de medições com aumento_pct > 80 nas últimas cinco."
            },
            {
                "nome": "n5_risco",
                "tipo": "int",
                "descricao": "Quantidade de medições que atendem a pelo menos um critério de risco nas últimas cinco."
            }
        ],
        "n_combinacoes_grade": n_combinacoes,
        "best_params": json_ready(busca.best_params_),
        "macro_f1_validacao": float(busca.best_score_),
        "macro_f1_teste": metrics["macro_f1"],
        "recall_falha_teste": metrics["recall_falha"],
        "classification_report": json_ready(metrics["classification_report"]),
        "confusion_matrix": metrics["confusion_matrix"],
        "confusion_matrix_labels": metrics["confusion_matrix_labels"],
        "feature_importances": feature_importances,
        "calculo_features": {
            "perda_pct": {
            "formula": "((sent - rcvd) / sent) * 100",
            "regra": "Calculada somente quando sent > 0."
            },
            "aumento_pct": {
            "formula": "((rtt_valido - mediana) / mediana) * 100",
            "regra": "Compara o RTT atual com a mediana do baseline."
            },
            "z_robusto": {
            "formula": "(rtt_valido - mediana) / (1.4826 * MAD)",
            "regra": "Se MAD = 0, retorna 0 quando RTT = mediana; caso contrário, usa (RTT - mediana) / max(IQR / 1.349, 1)."
            },
            "jitter_atual": {
            "formula": "Média das diferenças absolutas entre RTTs válidos consecutivos.",
            "regra": "Ignora RTTs inválidos e retorna ausente quando não há diferenças calculáveis."
            },
            "jitter_relativo": {
            "formula": "jitter_atual / jitter_tipico",
            "regra": "Se jitter_tipico = 0, retorna 1 quando ambos são zero e 3 quando o jitter atual é positivo."
            },
            "timeout_atual": {
            "formula": "1 se não há RTT válido ou perda_pct = 100; caso contrário, 0."
            },
            "n5_timeout": {
            "formula": "Soma dos timeouts nas últimas 5 medições do fluxo, incluindo a atual."
            },
            "n5_aumento80": {
            "formula": "Quantidade das últimas 5 medições com aumento_pct > 80."
            },
            "n5_risco": {
            "formula": "Quantidade das últimas 5 medições que atendem a pelo menos um critério de risco.",
            "criterios": [
                "2 <= z_robusto < 3.5",
                "30 <= aumento_pct <= 80",
                "jitter_relativo >= 3"
            ]
            },
            "regras_gerais": [
            "As medições são agrupadas por msm_id e probe_id e ordenadas por timestamp.",
            "As contagens usam até 5 medições disponíveis no início do histórico.",
            "Valores não calculáveis permanecem ausentes, exceto nos casos com tratamento específico descrito acima."
            ]
        },
        "horizonte_previsao": {
            "intervalo_minimo_segundos": 720,
            "intervalo_minimo_minutos": 12,
            "regra": "A classe futura corresponde à primeira medição do mesmo fluxo cujo timestamp seja maior ou igual ao timestamp atual acrescido de 720 segundos.",
            "tratamento_sem_medicao_futura": "A medição atual é removida do conjunto de dados quando não existe uma medição posterior que atenda ao horizonte mínimo."
        },
        "historico_necessario": {
            "identificacao_fluxo": [
            "msm_id",
            "probe_id"
            ],
            "dados_brutos_medicao": [
            "timestamp",
            "avg",
            "sent",
            "rcvd",
            "result"
            ],
            "janela_recente": {
            "quantidade_maxima": 5,
            "inclui_medicao_atual": True,
            "agrupamento": [
                "msm_id",
                "probe_id"
            ],
            "ordenacao": "timestamp crescente",
            "regra": "As features de contagem são recalculadas usando até cinco medições disponíveis do mesmo fluxo, incluindo a atual."
            },
            "recalculo_features": "As nove features devem ser calculadas antes de chamar o modelo, utilizando a medição atual, o histórico recente e os valores de referência necessários."
        },
        "saida": {
            "tipo": "classificacao",
            "descricao": "Classe prevista para o estado do fluxo de rede no horizonte futuro definido pelo projeto.",
            "classes": {
            "OK": "Nenhum critério de RISCO ou FALHA foi atendido.",
            "RISCO": "A medição atende a pelo menos um critério individual de risco e n5_risco >= 2.",
            "FALHA": "A medição apresenta perda_pct >= 10, n5_timeout >= 3, z_robusto >= 3.5 com RTT presente ou n5_aumento80 >= 2."
            },
            "prioridade_rotulagem": [
            "FALHA",
            "RISCO",
            "OK"
            ],
            "ordem_classes_modelo": [
            "FALHA",
            "OK",
            "RISCO"
            ],
            "ordem_matriz_confusao": [
            "OK",
            "RISCO",
            "FALHA"
            ]
        },
        "exemplo_entrada_saida": {
            "entrada": {
            "perda_pct": 0.0,
            "aumento_pct": -0.8133,
            "z_robusto": -2.2003,
            "jitter_atual": 0.0805,
            "jitter_relativo": 0.5089,
            "timeout_atual": 0,
            "n5_timeout": 0,
            "n5_aumento80": 0,
            "n5_risco": 0
            },
            "saida_prevista": "OK"
        },
        "regras_uso_baseline": {
            "periodo_origem": "Período A",
            "imutabilidade": "O baseline é calculado no Período A e permanece congelado durante o cálculo das métricas do Período B.",
            "agrupamento": ["msm_id", "probe_id"],
            "minimo_rtt_validos": 1500,
            "estatisticas_utilizadas": [
                "mediana",
                "MAD",
                "IQR",
                "jitter_tipico"
            ],
            "associacao": "Cada fluxo do Período B deve possuir exatamente uma linha correspondente no baseline, identificada por msm_id e probe_id.",
            "validacao": "Fluxos ausentes no baseline ou registros duplicados provocam ValueError.",
            "aplicacao": {
                "aumento_pct": "Compara o RTT atual com a mediana do baseline.",
                "z_robusto": "Utiliza a mediana, o MAD e, quando necessário, o IQR do baseline.",
                "jitter_relativo": "Compara o jitter atual com o jitter_tipico do baseline."
            }
        }


    }


def save_artifacts(familia, busca, metrics, n_combinacoes, joblib_name, metadata_name, grid_name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = build_metadata(familia, busca, metrics, n_combinacoes)

    joblib_path = OUTPUT_DIR / joblib_name
    metadata_path = OUTPUT_DIR / metadata_name
    grid_path = OUTPUT_DIR / grid_name

    joblib.dump(
        {
            "familia": familia,
            "modelo": busca.best_estimator_,
            "params": busca.best_params_,
            "features": list(FEATURES),
            "macro_f1_validacao": metadata["macro_f1_validacao"],
            "macro_f1_teste": metadata["macro_f1_teste"],
            "recall_falha_teste": metadata["recall_falha_teste"],
            "seed": SEED,
        },
        joblib_path,
    )

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    pd.DataFrame(busca.cv_results_).to_csv(grid_path, index=False)

    print(f"\nModelo salvo em: {joblib_path}")
    print(f"Metadados salvos em: {metadata_path}")
    print(f"Resultados da busca salvos em: {grid_path}")

    return {
        "joblib_path": joblib_path,
        "metadata_path": metadata_path,
        "grid_path": grid_path,
        "metadata": metadata,
    }
