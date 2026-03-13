from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import json
import time
import joblib
import numpy as np
import pandas as pd
from loguru import logger

# --- Constantes para validação de desempenho ---
# Definem quantas vezes cada parte do modelo será executada (repetições) para medir o tempo médio (benchmarking)
# Isso garante que a medição seja robusta e não distorcida por picos temporários do sistema.
GK_BENCH_REPEATS = 7     # Repetições para o gatekeeper (em modo "batch", avaliando todos de uma vez)
S2_BENCH_REPEATS = 3     # Repetições para o especialista (avaliando linha por linha, de forma detalhada)


@dataclass
class TwoStageConfig:
    """
    Configurações gerais para o inferenciador (quem faz a predição) de Dois Estágios.
    O primeiro estágio é o 'Gatekeeper' (rápido, genérico) e o segundo são os 'Especialistas' (lentos, precisos).
    """
    gatekeeper_model: str                  # Caminho para o modelo treinado do Gatekeeper (.pkl, .joblib)
    gatekeeper_features_file: str          # Arquivo texto com a lista de atributos (features) do Gatekeeper (1 por linha)
    specialist_map_json: str               # JSON ligando as saídas do Gatekeeper aos modelos Especialistas
    input_csv: str                         # Tabela CSV contendo os dados a serem classificados
    output_csv: str                        # Caminho e nome do arquivo CSV de saída (resultado das predições)
    fill_missing: float = 0.0              # Valor padrão usado para preencher colunas (features) que estão faltando
    gatekeeper_labelmap_json: Optional[str] = None  # (Opcional) Dicionário mapeando da saída original do GK para a chave correta do especialista


class TwoStageInferencer:
    """
    Classe principal de Inferência (predição/teste) da Arquitetura de Dois Estágios.
    O fluxo principal de inferência acontece aqui:
      1. Os dados chegam ao modelo.
      2. O Gatekeeper avalia todas as amostras rapidamente.
      3. Dependendo da classificação do Gatekeeper, cada amostra pode ser enviada para um 'Especialista'.
      4. O resultado final e as métricas de tempo (latência) são calculados.
    """
    def __init__(self, cfg: TwoStageConfig):
        self.cfg = cfg
        # Carrega o modelo de IA do Gatekeeper
        self.gatekeeper = self._load_gatekeeper(cfg.gatekeeper_model)
        # Carrega a lista de variáveis (features) necessárias para o Gatekeeper rodar
        self.gk_features = self._load_feature_list(cfg.gatekeeper_features_file)
        # Carrega o mapa/dicionário de modelos Especialistas baseados nas saídas possíveis do Gatekeeper
        self.spec_map, self.meta = self._load_specialists(cfg.specialist_map_json)
        
        # Carrega metadados que ajudam a traduzir/decodificar as classes
        self.class_encoding = self.meta.get("class_encoding") if self.meta else None
        self.classes_list = self.meta.get("classes") if self.meta else None
        self.target_col = self.meta.get("target_col") if self.meta else None

        # Tenta descobrir o arquivo 'labelmap' (mapeamento de labels) de forma automática 
        # caso não tenha sido explicitamente configurado no 'cfg'. Geralmente aplicável a problemas binários.
        lm_path: Optional[str] = cfg.gatekeeper_labelmap_json
        if not lm_path and self.classes_list and len(self.classes_list) <= 2:
            cand = [
                Path(cfg.specialist_map_json).parent / "gk_labelmap_unsw.json",
                Path("artifacts/gk_labelmap_unsw.json"),
                Path("artifacts/gk_labelmap.json"),
            ]
            for p in cand:
                if p.exists():
                    lm_path = str(p)
                    break
        # Carrega o mapa final
        self.labelmap = self._load_labelmap(lm_path)

    @staticmethod
    def _load_gatekeeper(path: str):
        """Carrega e retorna o arquivo serializado (joblib) contendo o modelo Gatekeeper."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Gatekeeper não encontrado: {p}")
        return joblib.load(p)

    @staticmethod
    def _load_feature_list(path: str) -> List[str]:
        """Lê um arquivo de texto linha a linha e retorna a lista de atributos (features)."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Arquivo de features do gatekeeper não encontrado: {p}")
        feats: List[str] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            # Ignora linhas em branco ou comentários
            if not s or s.startswith("#"):
                continue
            feats.append(s)
        return feats

    @staticmethod
    def _load_specialists(path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Abre o arquivo JSON `specialist_map` (dicionário associando saídas do Gatekeeper aos especialistas)
        e carrega em memória todos os modelos especialistas associados e suas respectivas features.
        """
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        specs: Dict[str, Any] = {}
        for cls_name, payload in d.get("specialists", {}).items():
            mpath = Path(payload["model_path"])
            if not mpath.exists():
                logger.warning(f"Modelo do especialista ausente para classe {cls_name}: {mpath}")
                continue
            
            model = joblib.load(mpath)
            feats = list(payload["features"])
            
            # Mapeia tudo por classe identificada no JSON
            specs[str(cls_name)] = {
                "model": model,
                "features": feats,
                "model_key": payload.get("model_key", ""),
                "feature_set_name": payload.get("feature_set_name", "")
            }
            
        if not specs:
            raise RuntimeError("Nenhum especialista carregado a partir do mapa.")
            
        meta = {
            "classes": d.get("classes") or [],
            "class_encoding": d.get("class_encoding") or {},
            "target_col": d.get("target_col", "")
        }
        return specs, meta

    @staticmethod
    def _load_labelmap(path: Optional[str]) -> Dict[str, str]:
        """
        Carrega um dicionário (JSON) usado para converter os labels internos/físicos que
        o Gatekeeper emite para labels ou strings padronizadas esperadas pelos especialistas.
        """
        if not path:
            return {}
        p = Path(path)
        if not p.exists():
            logger.warning(f"Label map não encontrado: {p}")
            return {}
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            # normaliza todas as chaves e valores como strings, prevenindo erros de tipo.
            return {str(k): str(v) for k, v in d.items()}
        except Exception as e:
            logger.warning(f"Falha ao ler label map {p}: {e}")
            return {}

    @staticmethod
    def _heuristic_bin_map(x: Any) -> Optional[str]:
        """
        Função de segurança (heurística) para casos binários:
        Converte uma classe textual em uma representação '0' ou '1'.
        Exemplo: 'benign' ou 'normal' torna-se '0' (tráfego ok).
        Outros, possivelmente maliciosos, tornam-se '1'.
        """
        try:
            if isinstance(x, (int, np.integer)):
                return str(int(x))
            s = str(x).strip().lower()
            if s in {"0", "1"}:
                return s
            if any(tok in s for tok in ("benign", "normal", "clean", "legit")):
                return "0"
            return "1"
        except Exception:
            return None

    def _decode_label(self, yhat: Any) -> Any:
        """
        Converte a predição bruta final (do especialista) para o texto/classe real do domínio.
        Ele tenta usar primeiramente a lista ou enumeração formal (class_encoding) antes de recorrer
        à função heurística binária.
        """
        # Tenta usar class_encoding explícito
        if self.class_encoding:
            try:
                key = str(int(yhat))
                if key in self.class_encoding:
                    return self.class_encoding[key]
            except Exception:
                pass
                
        # Tenta usar a lista de classes baseando-se por posição no array
        if self.classes_list is not None:
            try:
                idx = int(yhat)
                if 0 <= idx < len(self.classes_list):
                    return self.classes_list[idx]
            except Exception:
                pass
                
        # Caso falhe as abordagens acima, usa fallback da heurística binária 
        hb = self._heuristic_bin_map(yhat)
        if hb is not None:
            return int(hb)
            
        # Se não mapeou para nada, apenas retorna o predição bruta
        return yhat

    def _ensure_columns(self, df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """
        Garante que o DataFrame (df) possuirá exatamente as colunas solicitadas (cols).
        Se a coluna não tiver sido provida, será criada e preenchida com um valor default.
        Isso é vital, pois o modelo de Machine Learning requer uma ordem e quantidade exata de features.
        """
        df = df.copy()
        for c in cols:
            if c not in df.columns:
                df[c] = self.cfg.fill_missing
        return df[cols]

    def predict_csv(self) -> Tuple[float, float, float]:
        """
        O fluxo principal da inferência para um lote de dados contidos em um arquivo CSV.
        Retorna a métrica de de latência (tempo gasto em média por linha).
        """
        # 1. Carrega os dados em um DataFrame (tabela).
        df = pd.read_csv(self.cfg.input_csv)
        n = df.shape[0]
        if n == 0:
            raise ValueError("input_csv não possui linhas.")

        # 2. Etapa 1 — Gatekeeper: Pega a matriz correta de features para o Gatekeeper
        Xgk = self._ensure_columns(df, self.gk_features)

        # Alguns modelos retornam só as previsões, outros previsões+latência. Tentamos ambos.
        _res = self.gatekeeper.predict(Xgk)
        if isinstance(_res, tuple):
            gk_pred = _res[0]
        else:
            gk_pred = _res

        # Transforma o array em um formato 1-D simples para facilitar as interações futuras.
        gk_pred = np.asarray(gk_pred).ravel()

        # Roda um ciclo rápido apenas como "warm-up" (aquecimento)
        # Isso acorda as caches do processador e otimizações JIT antes de contar o tempo real.
        _ = self.gatekeeper.predict(Xgk.iloc[: min(512, len(Xgk))])

        # Benchmark oficial do Gatekeeper no processamento do Batch inteiro. 
        # Roda o modelo N vezes e pega a execução mais rápida.
        gk_best_ns = None
        for _rep in range(GK_BENCH_REPEATS):
            ns0 = time.perf_counter_ns()
            _ = self.gatekeeper.predict(Xgk)
            ns1 = time.perf_counter_ns()
            dt = ns1 - ns0
            gk_best_ns = dt if (gk_best_ns is None or dt < gk_best_ns) else gk_best_ns
            
        # Calcula a média por amostra em milissegundos
        gk_ms = (gk_best_ns / 1e6) / max(1, n)

        # 3. Etapa 2 — Especialistas: Itera sobre os exemplos linha-a-linha individualmente
        final_pred: List[int] = []
        spec_used: List[str] = []
        spec_set: List[str] = []
        stage2_times: List[float] = []
        gk_mapped: List[str] = []

        for i, gp in enumerate(gk_pred):
            # 3.1) Se existir no Gatekeeper alguma labelmap configurada, converte o label dele 
            # de acordo com o padrão do especialista aplicável.
            cls: Optional[str] = None
            if self.labelmap:
                key = str(gp)
                mapped = self.labelmap.get(key)
                if mapped is not None:
                    cls = str(mapped)

            # 3.2) Se esse mapeamento explicitamente não aconteceu, toma uma decisão de fallback default
            if cls is None:
                if self.classes_list and len(self.classes_list) > 2:
                    cls = str(gp)  # Modo Multi-classe preserva a saída como string
                else:
                    cls = self._heuristic_bin_map(gp)  # Modo binário aplica binning heurístico

            if cls is None:
                cls = str(gp)

            # Guarda para debug qual foi a saída que o script achou ter recebido do GK.
            gk_mapped.append(cls)

            # Tenta pegar qual o especialista vinculado com esta label no Json specialist_map_json
            spec = self.spec_map.get(cls)
            
            # Se não localizar Especialista associado...
            if spec is None:
                # O Gatekeeper não repassou para nenhum especialista. O próprio modelo Gatekeeper 'fechou' o veredito.
                if self.classes_list and len(self.classes_list) > 2:
                    final_pred.append(str(cls))
                else:
                    try:
                        yhat_int = int(cls)
                    except Exception:
                        h = self._heuristic_bin_map(cls)
                        yhat_int = int(h) if h is not None else 0
                    final_pred.append(yhat_int)
                
                # Como não foi pro Especialista, latência do stage 2 será 0ms pra essa amostra finalizada cedo
                spec_used.append("fallback_gk")
                spec_set.append("NA")
                stage2_times.append(0.0)
                continue

            # Se encontrou um especialista, ele roda localmente!
            feats = spec["features"]
            model = spec["model"]
            row_df = df.iloc[[i]]
            Xsp = self._ensure_columns(row_df, feats)

            best_ns = None
            yhat = None
            # Benchmark linha por linha em repetições robustas
            for _rep in range(S2_BENCH_REPEATS):
                ns2 = time.perf_counter_ns()
                yhat = model.predict(Xsp)[0]
                ns3 = time.perf_counter_ns()
                dt = ns3 - ns2
                best_ns = dt if (best_ns is None or dt < best_ns) else best_ns

            # Decode final p/ array e grava logs da amostra do "especialista"
            decoded = self._decode_label(yhat)
            final_pred.append(decoded)
            spec_used.append(spec.get("model_key", ""))
            spec_set.append(spec.get("feature_set_name", ""))
            stage2_times.append(best_ns / 1e6)  # milissegundos (ms)

        # 4. Compilando as latências
        stage2_ms = float(np.mean(stage2_times)) if stage2_times else 0.0
        total_ms = gk_ms + stage2_ms

        # 5. Salva no novo DataFrame e exporta para o CSV requisitado.
        out = df.copy()
        out["pred_gatekeeper"] = gk_pred
        out["pred_gatekeeper_mapped"] = gk_mapped
        out["pred_final"] = final_pred
        out["specialist_model"] = spec_used
        out["specialist_featureset"] = spec_set
        out["latency_ms_stage1"] = round(gk_ms, 6)
        out["latency_ms_stage2"] = [round(x, 6) for x in stage2_times]
        out["latency_ms_total_est"] = round(total_ms, 6)

        Path(self.cfg.output_csv).parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(self.cfg.output_csv, index=False)
        
        # Loga os detalhes da performance
        logger.success(f"Predições salvas em {self.cfg.output_csv}")
        logger.info(
            f"Latência média — Gatekeeper: {gk_ms:.6f} ms | "
            f"Especialista: {stage2_ms:.6f} ms | Total: {total_ms:.6f} ms/linha"
        )
        return gk_ms, stage2_ms, total_ms
