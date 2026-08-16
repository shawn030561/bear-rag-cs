"""检索器：基于 BM25 的产品知识检索（中文友好，字符 bigram + 单字分词）。"""
import json
import math
import re
from collections import Counter

from config import config


def tokenize(text):
    """中文友好分词：中文字符单字 + 连续字母数字串 + 中文 bigram。"""
    text = (text or "").lower()
    tokens = []
    for ch in text:
        if "一" <= ch <= "鿿":
            tokens.append(ch)
    tokens.extend(re.findall(r"[a-z0-9]+", text))
    cjk = [ch for ch in text if "一" <= ch <= "鿿"]
    tokens.extend(cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1))
    return tokens


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.N = len(docs)
        self.avgdl = sum(len(d) for d in docs) / max(1, self.N)
        self.df = Counter()
        for d in docs:
            for t in set(d):
                self.df[t] += 1

    def scores(self, query_tokens):
        out = []
        for d in self.docs:
            tf = Counter(d)
            dl = len(d)
            s = 0.0
            for t in query_tokens:
                if t not in self.df:
                    continue
                idf = math.log(1 + (self.N - self.df[t] + 0.5) / (self.df[t] + 0.5))
                f = tf.get(t, 0)
                s += idf * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            out.append(s)
        return out


def _product_doc_text(p):
    parts = [
        (p.get("name", "") + " ") * 3,  # 名称加权，提升匹配优先级
        " ".join(p.get("keywords", [])),
        " ".join(p.get("selling_points", [])),
        " ".join(p.get("target_users", [])),
        p.get("competitive_advantage", ""),
        " ".join(p.get("comparisons", {}).keys()),
        " ".join(f"{k} {v}" for k, v in (p.get("specs") or {}).items()),
        " ".join(f"{f['q']} {f['a']}" for f in p.get("faq", [])),
    ]
    return " ".join(parts)


class Retriever:
    def __init__(self, products_file=None):
        self.products_file = products_file or config.PRODUCTS_FILE
        self.products = json.loads(self.products_file.read_text(encoding="utf-8"))["products"]
        self.docs = [_product_doc_text(p) for p in self.products]
        self.doc_tokens = [tokenize(d) for d in self.docs]
        self.bm25 = BM25(self.doc_tokens)

    def search(self, query, top_k=3):
        q = tokenize(query)
        scores = self.bm25.scores(q)
        ranked = sorted(enumerate(scores), key=lambda x: -x[1])
        nonzero = [(i, s) for i, s in ranked if s > 0]
        if nonzero:
            ranked = nonzero
        results = []
        for i, s in ranked[:top_k]:
            results.append({"product": self.products[i], "score": round(s, 4)})
        return results
